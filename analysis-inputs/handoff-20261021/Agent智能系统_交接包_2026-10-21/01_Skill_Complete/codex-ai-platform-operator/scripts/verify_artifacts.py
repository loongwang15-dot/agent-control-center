#!/usr/bin/env python3
"""Verify local artifacts listed in a JSON manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
from pathlib import Path


def sniff_media_type(path: Path, head: bytes) -> str | None:
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    if head.startswith(b"%PDF-"):
        return "application/pdf"
    if head.startswith(b"PK\x03\x04"):
        return "application/zip"
    return mimetypes.guess_type(path.name)[0]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--root",
        type=Path,
        help="Optional root; relative paths resolve here instead of manifest directory",
    )
    parser.add_argument("--allow-outside-root", action="store_true")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        report = {"status": "BLOCKED", "error": str(error)}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    entries = manifest.get("artifacts") if isinstance(manifest, dict) else manifest
    if not isinstance(entries, list):
        report = {
            "status": "BLOCKED",
            "error": "manifest must be an array or contain artifacts[]",
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    root = (args.root or args.manifest.parent).resolve()
    results = []
    seen: dict[str, int] = {}
    has_missing = False
    has_partial = False
    for index, entry in enumerate(entries):
        if isinstance(entry, str):
            raw_path, expected = entry, None
        elif isinstance(entry, dict):
            raw_path, expected = entry.get("path"), entry.get("sha256")
        else:
            results.append(
                {
                    "index": index,
                    "status": "FAIL",
                    "error": "entry must be a path string or object",
                }
            )
            has_partial = True
            continue
        if not isinstance(raw_path, str) or not raw_path.strip():
            results.append(
                {"index": index, "status": "FAIL", "error": "missing path"}
            )
            has_partial = True
            continue
        path = Path(raw_path)
        path = path if path.is_absolute() else root / path
        path = path.resolve()
        if not args.allow_outside_root and not path.is_relative_to(root):
            results.append(
                {
                    "index": index,
                    "path": str(path),
                    "status": "FAIL",
                    "error": "path is outside root",
                }
            )
            has_partial = True
            continue
        if not path.is_file():
            results.append(
                {
                    "index": index,
                    "path": str(path),
                    "status": "FAIL",
                    "error": "file not found",
                }
            )
            has_missing = True
            continue
        with path.open("rb") as handle:
            head = handle.read(32)
        digest = sha256(path)
        duplicate_of = seen.get(digest)
        seen.setdefault(digest, index)
        item = {
            "index": index,
            "path": str(path),
            "status": "PASS",
            "size": path.stat().st_size,
            "sha256": digest,
            "media_type": sniff_media_type(path, head),
            "duplicate_of": duplicate_of,
        }
        if expected and str(expected).lower() != digest:
            item["status"] = "FAIL"
            item["error"] = "SHA-256 mismatch"
            has_partial = True
        results.append(item)
    status = "FAIL" if has_missing else "PARTIAL" if has_partial else "PASS"
    report = {
        "schema_version": "1.0",
        "manifest": str(args.manifest.resolve()),
        "root": str(root),
        "status": status,
        "artifacts": results,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
