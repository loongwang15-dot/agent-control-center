"""Export reviewed source, frontend build and clean vault seeds; never runtime data.

Uses only the Python standard library. The output has no .git directory and
includes an UPSTREAM.json SHA-256 manifest understood by install.ps1.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from datetime import datetime, timezone
import zipfile


ROOT = Path(__file__).resolve().parent
UPSTREAM_URL = "https://github.com/agentscope-ai/agentscope.git"
UPSTREAM_COMMIT = "58da57a565832ac3710d0f22318a5d0ee326a406"
EXCLUDED_PARTS = {
    ".git", ".venv", "venv", ".cache", "node_modules", "runtime", "analysis-inputs",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox",
    "workspaces", "blobs", ".agent_memory", "vault-history",
}
ROOT_FILES = (
    "install.ps1", "start.ps1", "stop.ps1", "启动总控台.cmd", "停止总控台.cmd",
    "README.md", "pack_source.py", ".gitignore", "部署验收记录_2026-10-21.md",
)
CONTROL_FILES = (
    "__init__.py", "main.py", "vault.py", "requirements.txt", "requirements.lock.txt", "test_main.py", "test_vault.py", "browser-smoke.cjs",
)
VAULT_FILES = (
    "Obsidian知识库/00_使用说明.md",
    "Obsidian知识库/10_项目/Agent智能系统.md",
    "Obsidian知识库/.obsidian/app.json",
    "Obsidian知识库/知识目录.base",
)
REQUIRED_SOURCES = {
    "agentscope/LICENSE", "agentscope/pyproject.toml",
    "agentscope/src/agentscope/_version.py", "agentscope/src/agentscope/app/_app.py",
    "agentscope/examples/web_ui/frontend/package.json",
    "agentscope/examples/web_ui/frontend/src/App.tsx",
    "agentscope/examples/web_ui/frontend/src/api/vault.ts",
    "agentscope/examples/web_ui/frontend/src/pages/vault/index.tsx",
    "agentscope/examples/web_ui/frontend/dist/index.html",
    "control/main.py", "control/vault.py", "control/requirements.txt", "control/requirements.lock.txt",
}


def excluded(relative: str) -> bool:
    parts = PurePosixPath(relative).parts
    if any(part.lower() in EXCLUDED_PARTS or part.endswith(".egg-info") for part in parts):
        return True
    name = parts[-1].lower()
    if name == ".env" or (name.startswith(".env.") and name not in {".env.example", ".env.sample", ".env.template"}):
        return True
    return name.endswith((".pyc", ".pyo", ".log", ".key", ".pem", ".sqlite", ".sqlite3", ".db"))


def checked_path(relative: str) -> Path:
    pure = PurePosixPath(relative)
    if not relative or "\\" in relative or pure.is_absolute() or any(p in {".", ".."} for p in pure.parts):
        raise ValueError(f"Unsafe source path: {relative}")
    if ":" in relative or excluded(relative):
        raise ValueError(f"Excluded source path: {relative}")
    target = ROOT
    for part in pure.parts:
        target = target / part
        details = target.lstat()
        if target.is_symlink() or getattr(details, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError(f"Refusing a symbolic link or reparse point: {relative}")
    if not target.is_file():
        raise ValueError(f"Missing source file: {relative}")
    return target


def git(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT / "agentscope"), *arguments],
        check=True, capture_output=True, encoding="utf-8",
    )
    return completed.stdout


def select_sources() -> tuple[set[str], list[str], bool]:
    upstream = ROOT / "agentscope"
    if (upstream / ".git").exists():
        if git("rev-parse", "HEAD").strip() != UPSTREAM_COMMIT:
            raise ValueError("Upstream HEAD is not the pinned commit. Nothing was packaged.")
        remote = git("remote", "get-url", "origin").strip()
        if remote.rstrip("/").removesuffix(".git") not in {
            "https://github.com/agentscope-ai/agentscope", "git@github.com:agentscope-ai/agentscope",
        }:
            raise ValueError("Unexpected upstream origin. Nothing was packaged.")
        # Only tracked upstream files enter the export. Newly created frontend
        # code is added below; unrelated untracked files are never swept in.
        names = {"agentscope/" + name for name in git("ls-files", "-z").split("\0") if name}
        changes = ["agentscope/" + name for name in git("diff", "--name-only", "HEAD", "-z").split("\0") if name]
        repacked = False
    else:
        manifest = json.loads((ROOT / "UPSTREAM.json").read_text(encoding="utf-8-sig"))
        if manifest.get("project") != "agent-control-console" or manifest.get("upstream", {}).get("commit") != UPSTREAM_COMMIT:
            raise ValueError("Repacking a source archive requires its matching UPSTREAM.json.")
        names = {entry["path"] for entry in manifest["files"] if entry["path"].startswith("agentscope/")}
        changes = list(manifest.get("local_changes", []))
        repacked = True

    for folder in (upstream / "examples/web_ui/frontend/src", upstream / "examples/web_ui/frontend/dist"):
        if not folder.is_dir():
            raise ValueError(f"Required frontend folder is absent: {folder}")
        for directory, subdirectories, filenames in os.walk(folder, followlinks=False):
            subdirectories[:] = [name for name in subdirectories if name.lower() not in EXCLUDED_PARTS]
            for filename in filenames:
                path = Path(directory, filename)
                relative = path.relative_to(ROOT).as_posix()
                if folder.name == "src" and path.suffix.lower() not in {".ts", ".tsx", ".css", ".json", ".svg"}:
                    continue
                if not excluded(relative):
                    if relative not in names and folder.name == "src":
                        changes.append(relative)
                    names.add(relative)

    names.update(ROOT_FILES)
    names.update("control/" + name for name in CONTROL_FILES)
    names.update(VAULT_FILES)
    names = {name for name in names if not excluded(name)}
    missing = REQUIRED_SOURCES - names
    if missing:
        raise ValueError(f"Package is missing required customized sources: {sorted(missing)}")
    for name in names:
        checked_path(name)
    return names, sorted(set(changes)), repacked


def build_package(output: Path) -> dict:
    names, local_changes, repacked = select_sources()
    output = output.resolve()
    if output.exists():
        raise ValueError(f"Output already exists; use a new filename: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".partial")
    if temporary.exists():
        raise ValueError(f"A partial archive already exists; inspect it before retrying: {temporary}")
    entries = []
    try:
        with zipfile.ZipFile(temporary, mode="x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name in sorted(names):
                data = checked_path(name).read_bytes()
                archive.writestr(name, data)
                entries.append({
                    "path": name, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data),
                    "verify_on_install": not name.startswith("Obsidian知识库/"),
                })
            manifest = {
                "schema_version": 1,
                "project": "agent-control-console",
                "exported_at_utc": datetime.now(timezone.utc).isoformat(),
                "upstream": {"repository": UPSTREAM_URL, "commit": UPSTREAM_COMMIT, "version": "2.0.11dev", "license": "Apache-2.0"},
                "local_changes": local_changes,
                "local_additions": [*ROOT_FILES, *("control/" + name for name in CONTROL_FILES), *VAULT_FILES],
                "repacked_without_git": repacked,
                "verification_note": "Hashes check package integrity; this manifest is not a digital signature or independent proof of upstream provenance.",
                "files": entries,
            }
            archive.writestr("UPSTREAM.json", json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
        # Re-read every exported byte and the entry names before making the ZIP
        # available. This verifies the artifact, not the live source a second time.
        with zipfile.ZipFile(temporary) as archive:
            if set(archive.namelist()) != names | {"UPSTREAM.json"}:
                raise ValueError("Archive contents differ from the selected source manifest.")
            for entry in entries:
                if hashlib.sha256(archive.read(entry["path"])).hexdigest() != entry["sha256"]:
                    raise ValueError(f"Archive hash check failed: {entry['path']}")
        temporary.rename(output)
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise
    return {"path": str(output), "files": len(entries), "bytes": output.stat().st_size, "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "release" / ("Agent-Control-Console-source-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + ".zip"))
    arguments = parser.parse_args()
    try:
        print(json.dumps(build_package(arguments.output), ensure_ascii=False, indent=2))
    except (OSError, ValueError, subprocess.CalledProcessError, KeyError) as error:
        print(f"Package failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
