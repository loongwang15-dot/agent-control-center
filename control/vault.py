"""A local Markdown vault API; retrieval here is literal full-text search.

The vault is intentionally separate from AgentScope runtime state. Existing
notes use optimistic concurrency, and previous bytes are retained outside it.
"""

from __future__ import annotations

import hashlib
import os
import re
import stat
import threading
import unicodedata
import uuid
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote

import yaml
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel


MAX_ATTACHMENT_BYTES = 20 * 1024 * 1024
ATTACHMENT_FOLDER = "attachments"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
IMAGE_MIMES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
_INVALID_COMPONENT = re.compile(r'[<>:"|?*\x00-\x1f\x7f]')
_RESERVED_NAME = re.compile(r"^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)", re.I)


class NoteWrite(BaseModel):
    path: str
    content: str
    expected_sha256: str | None = None


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _is_link(path: Path) -> bool:
    """Treat Windows junctions/reparse points as links, too."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & 0x400
    )


def _relative_path(value: str, *, allow_empty: bool = False) -> PurePosixPath:
    if value == "" and allow_empty:
        return PurePosixPath()
    if not value or "\\" in value or value.startswith("/"):
        raise HTTPException(400, "Use a relative path with forward slashes.")
    parts = value.split("/")
    if any(
        not part
        or part in {".", ".."}
        or part.startswith(".")
        or part.endswith((" ", "."))
        or _INVALID_COMPONENT.search(part)
        or _RESERVED_NAME.match(part)
        for part in parts
    ):
        raise HTTPException(400, "The path contains a forbidden component.")
    return PurePosixPath(*parts)


def _under_root(base: Path, relative: PurePosixPath) -> Path:
    """Resolve without trusting symlinks, junctions, or caller path syntax."""
    cursor = base
    if any(_is_link(part) for part in (base, *base.parents)):
        raise HTTPException(400, "Symbolic links and junctions are not allowed.")
    if base.exists() and not base.is_dir():
        raise HTTPException(400, "The configured storage root is not a directory.")
    for part in relative.parts:
        if cursor.exists() and not cursor.is_dir():
            raise HTTPException(400, "A parent path is not a directory.")
        cursor = cursor / part
        if _is_link(cursor):
            raise HTTPException(400, "Symbolic links and junctions are not allowed.")
    try:
        cursor.resolve(strict=False).relative_to(base.resolve(strict=False))
    except (ValueError, OSError, RuntimeError):
        raise HTTPException(400, "The path must stay inside the vault.") from None
    return cursor


def _metadata(content: str) -> dict[str, Any]:
    """Read safe YAML while preserving the original source, including errors."""
    lines = content.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = next(
        (i for i in range(1, min(len(lines), 1000)) if lines[i].strip() in {"---", "..."}),
        None,
    )
    if end is None:
        return {}
    frontmatter = "\n".join(lines[1:end])
    if len(frontmatter) > 65536:
        return {}
    try:
        parsed = yaml.safe_load(frontmatter)
    except (yaml.YAMLError, ValueError, RecursionError):
        return {}
    if not isinstance(parsed, dict):
        return {}
    remaining = [2000]

    def clean(value: Any, seen: set[int], depth: int = 0) -> Any:
        remaining[0] -= 1
        if depth > 8 or remaining[0] < 0:
            return None
        if value is None or isinstance(value, (str, bool, int)):
            return value
        if isinstance(value, float):
            return value if value == value and abs(value) != float("inf") else None
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if id(value) in seen:
            return None
        nested = seen | {id(value)}
        if isinstance(value, dict):
            return {str(k): clean(v, nested, depth + 1) for k, v in value.items()}
        if isinstance(value, list):
            return [clean(v, nested, depth + 1) for v in value]
        return str(value)

    return clean(parsed, set())


def _title(content: str, metadata: dict[str, Any], path: Path) -> str:
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    match = re.search(r"^#\s+(.+?)\s*#*\s*$", content, re.MULTILINE)
    return match.group(1).strip() if match else path.stem


def _tags(metadata: dict[str, Any]) -> list[str]:
    value = metadata.get("tags", [])
    if isinstance(value, str):
        return [tag.lstrip("#") for tag in re.split(r"[,\s]+", value) if tag]
    if isinstance(value, list):
        return [str(tag).lstrip("#") for tag in value if isinstance(tag, (str, int))]
    return []


def _image_type(header: bytes) -> tuple[str, str] | None:
    if len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR":
        return "image/png", ".png"
    if len(header) >= 4 and header[:3] == b"\xff\xd8\xff":
        return "image/jpeg", ".jpg"
    if len(header) >= 13 and header[:6] in {b"GIF87a", b"GIF89a"}:
        return "image/gif", ".gif"
    if (
        len(header) >= 16
        and header[:4] == b"RIFF"
        and header[8:12] == b"WEBP"
        and header[12:16] in {b"VP8 ", b"VP8L", b"VP8X"}
    ):
        return "image/webp", ".webp"
    return None


def _walk_files(root: Path, *, skip_attachments: bool = False):
    if not root.is_dir() or _is_link(root):
        return
    for directory, directories, filenames in os.walk(root, followlinks=False):
        parent = Path(directory)
        directories[:] = [
            name
            for name in directories
            if not name.startswith(".")
            and not _is_link(parent / name)
            and (not skip_attachments or name.casefold() != ATTACHMENT_FOLDER)
        ]
        for name in filenames:
            path = parent / name
            if not name.startswith(".") and not _is_link(path) and path.is_file():
                yield path


def create_vault_router(vault_root: Path, history_root: Path | None = None) -> APIRouter:
    """Build API routes without creating or populating a vault on startup."""
    root = Path(os.path.abspath(vault_root))
    history = Path(os.path.abspath(history_root or root.parent / "runtime" / "vault-history"))
    try:
        history.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        pass
    else:
        raise ValueError("History must be stored outside the knowledge vault.")
    router = APIRouter(prefix="/control/vault", tags=["Local Markdown vault"])
    write_lock = threading.RLock()

    def note_path(value: str) -> tuple[PurePosixPath, Path]:
        relative = _relative_path(value)
        if relative.suffix.casefold() != ".md" or relative.parts[0].casefold() == ATTACHMENT_FOLDER:
            raise HTTPException(400, "Notes must be Markdown files outside attachments/.")
        return relative, _under_root(root, relative)

    def read_note(path: Path, relative: str) -> dict[str, Any]:
        if not path.is_file():
            raise HTTPException(404, "Note not found.")
        raw = path.read_bytes()
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(400, "The note must use UTF-8 encoding.") from None
        return {
            "path": relative,
            "content": content,
            "sha256": _digest(raw),
            "metadata": _metadata(content),
        }

    @router.get("/status")
    def vault_status():
        _under_root(root, PurePosixPath())
        notes = sum(1 for p in _walk_files(root, skip_attachments=True) if p.suffix.casefold() == ".md")
        attachments = sum(
            1
            for p in _walk_files(root / ATTACHMENT_FOLDER)
            if p.suffix.casefold() in IMAGE_EXTENSIONS
        )
        return {
            "name": root.name,
            "root": str(root),
            "exists": root.is_dir(),
            "note_count": notes,
            "attachment_count": attachments,
        }

    @router.get("/notes")
    def list_notes(query: str = "", folder: str = ""):
        relative = _relative_path(folder, allow_empty=True)
        if relative.parts and relative.parts[0].casefold() == ATTACHMENT_FOLDER:
            raise HTTPException(400, "attachments/ is not a note folder.")
        start = _under_root(root, relative)
        if start.exists() and not start.is_dir():
            raise HTTPException(400, "folder must name a directory.")
        terms = query.casefold().split()
        items = []
        for path in _walk_files(start, skip_attachments=True):
            if path.suffix.casefold() != ".md":
                continue
            relative_name = path.relative_to(root).as_posix()
            try:
                _relative_path(relative_name)
                _under_root(root, PurePosixPath(relative_name))
                note = read_note(path, relative_name)
                info = path.stat()
            except (OSError, HTTPException):
                continue
            if terms and not all(term in (relative_name + "\n" + note["content"]).casefold() for term in terms):
                continue
            metadata = note["metadata"]
            items.append({
                "path": relative_name,
                "title": _title(note["content"], metadata, path),
                "project": metadata.get("project", "") if isinstance(metadata.get("project", ""), str) else "",
                "status": metadata.get("status", "") if isinstance(metadata.get("status", ""), str) else "",
                "tags": _tags(metadata),
                "updated_at": datetime.fromtimestamp(info.st_mtime, timezone.utc).isoformat(),
                "size": info.st_size,
            })
        items.sort(key=lambda item: (item["updated_at"], item["path"]), reverse=True)
        return {"items": items, "total": len(items)}

    @router.get("/note")
    def get_note(path: str):
        relative, target = note_path(path)
        return read_note(target, relative.as_posix())

    @router.put("/note")
    def put_note(body: NoteWrite):
        relative, target = note_path(body.path)
        raw = body.content.encode("utf-8")
        with write_lock:
            target = _under_root(root, relative)
            existed = target.exists()
            if existed and not target.is_file():
                raise HTTPException(400, "The note path is not a file.")
            previous = target.read_bytes() if existed else None
            if existed and (body.expected_sha256 is None or body.expected_sha256 != _digest(previous)):
                raise HTTPException(409, "The note changed. Reload it before saving.")
            if not existed and body.expected_sha256 is not None:
                raise HTTPException(409, "The note no longer exists. Reload before saving.")
            target.parent.mkdir(parents=True, exist_ok=True)
            target = _under_root(root, relative)
            if previous is not None and previous != raw:
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                backup_relative = relative.parent / f"{target.stem}.{stamp}-{uuid.uuid4().hex[:12]}.md"
                backup = _under_root(history, backup_relative)
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup = _under_root(history, backup_relative)
                with backup.open("xb") as handle:
                    handle.write(previous)
            temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
            try:
                with temporary.open("xb") as handle:
                    handle.write(raw)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
        return {
            "path": relative.as_posix(),
            "content": body.content,
            "sha256": _digest(raw),
            "metadata": _metadata(body.content),
            "created": not existed,
        }

    @router.post("/attachments", status_code=201)
    async def upload_attachment(file: UploadFile = File(...)):
        content = bytearray()
        try:
            while chunk := await file.read(65536):
                if len(content) + len(chunk) > MAX_ATTACHMENT_BYTES:
                    raise HTTPException(413, "Images must be at most 20 MiB.")
                content.extend(chunk)
            detected = _image_type(bytes(content[:32]))
            if detected is None:
                raise HTTPException(400, "Only PNG, JPEG, GIF and WebP image headers are accepted.")
            mime, extension = detected
            declared = (file.content_type or "").split(";", 1)[0].strip().lower()
            if declared not in {"", "application/octet-stream", mime}:
                raise HTTPException(400, "The declared image type does not match its file header.")
            filename = re.split(r"[/\\]", file.filename or "image")[-1]
            stem = unicodedata.normalize("NFKC", Path(filename).stem)
            stem = _INVALID_COMPONENT.sub("-", stem).strip(" ._")[:80] or "image"
            stem = re.sub(r"[^\w .-]", "-", stem)
            if _RESERVED_NAME.match(stem):
                stem = "image-" + stem
            name = f"{stem}-{uuid.uuid4().hex[:16]}{extension}"
            relative = PurePosixPath(ATTACHMENT_FOLDER) / name
            with write_lock:
                target = _under_root(root, relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target = _under_root(root, relative)
                with target.open("xb") as handle:
                    handle.write(content)
            relative_name = relative.as_posix()
            return {
                "path": relative_name,
                "name": name,
                "url": "/control/vault/attachment?path=" + quote(relative_name, safe=""),
                "markdown": f"![[{relative_name}]]",
            }
        finally:
            await file.close()

    @router.get("/attachment")
    def get_attachment(path: str):
        relative = _relative_path(path)
        if (
            len(relative.parts) < 2
            or relative.parts[0] != ATTACHMENT_FOLDER
            or relative.suffix.casefold() not in IMAGE_EXTENSIONS
        ):
            raise HTTPException(400, "Only supported images inside attachments/ can be served.")
        target = _under_root(root, relative)
        if not target.is_file():
            raise HTTPException(404, "Attachment not found.")
        if target.stat().st_size > MAX_ATTACHMENT_BYTES:
            raise HTTPException(413, "Images must be at most 20 MiB.")
        with target.open("rb") as handle:
            detected = _image_type(handle.read(32))
        if detected is None:
            raise HTTPException(400, "The attachment has an unsupported image header.")
        mime, extension = detected
        if relative.suffix.casefold() not in ({".jpg", ".jpeg"} if extension == ".jpg" else {extension}):
            raise HTTPException(400, "The file extension does not match its image header.")
        return FileResponse(
            target,
            media_type=mime,
            filename=target.name,
            content_disposition_type="inline",
            headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "no-store"},
        )

    return router
