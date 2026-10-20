#!/usr/bin/env python3
"""Read-only local capability check for codex-ai-platform-operator."""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
from pathlib import Path

SKILL_ID = "codex-ai-platform-operator"
CONTINUITY_FILES = [
    "agent-memory/00_PROJECT_BRIEF.md",
    "agent-memory/01_CURRENT_STATE.md",
    "agent-memory/02_DECISIONS.md",
    "agent-memory/03_NEXT_ACTION.md",
    "agent-memory/04_EVIDENCE_INDEX.md",
    "agent-memory/05_HANDOFF_LOG.md",
]


def run_version(command: list[str]) -> dict:
    executable = shutil.which(command[0])
    result = {
        "found": bool(executable),
        "path": executable,
        "version": None,
        "error": None,
    }
    if not executable:
        return result
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        output = (completed.stdout or completed.stderr).strip()
        result["version"] = output.splitlines()[0][:240] if output else ""
        if completed.returncode != 0:
            result["error"] = f"exit code {completed.returncode}"
    except (OSError, subprocess.SubprocessError) as error:
        result["error"] = str(error)
    return result


def inspect_mcp_config(path: Path) -> dict:
    if not path.is_file():
        return {
            "path": str(path),
            "exists": False,
            "playwright_section": False,
            "extension_flag": False,
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    start = text.find("[mcp_servers.playwright]")
    if start >= 0:
        next_section = re.search(r"(?m)^\[", text[start + 1 :])
        section = (
            text[start : start + 1 + next_section.start()]
            if next_section
            else text[start:]
        )
    else:
        section = ""
    return {
        "path": str(path),
        "exists": True,
        "playwright_section": start >= 0,
        "extension_flag": "--extension" in section,
    }


def skill_locations(project_root: Path) -> list[dict]:
    candidates = [
        Path(__file__).resolve().parents[1] / "SKILL.md",
        project_root / ".agents" / "skills" / SKILL_ID / "SKILL.md",
        Path.home() / ".agents" / "skills" / SKILL_ID / "SKILL.md",
        Path.home() / ".codex" / "skills" / SKILL_ID / "SKILL.md",
        project_root / "skills" / SKILL_ID / "SKILL.md",
    ]
    unique = {}
    for path in candidates:
        unique.setdefault(str(path.resolve()), path.is_file())
    return [
        {"path": path, "exists": exists}
        for path, exists in sorted(unique.items())
    ]


def inspect_continuity(project_root: Path) -> dict:
    guidance = project_root / "AGENTS.md"
    files = []
    for relative in CONTINUITY_FILES:
        path = project_root / relative
        files.append(
            {
                "path": relative,
                "exists": path.is_file(),
                "size": path.stat().st_size if path.is_file() else None,
            }
        )
    detected = guidance.is_file() or any(item["exists"] for item in files)
    missing = [item["path"] for item in files if not item["exists"]]
    if guidance.is_file() and not missing:
        status = "PASS"
    elif detected:
        status = "PARTIAL"
    else:
        status = "NOT_DETECTED"
    return {
        "status": status,
        "agents_md": {
            "path": "AGENTS.md",
            "exists": guidance.is_file(),
            "size": guidance.stat().st_size if guidance.is_file() else None,
        },
        "memory_files": files,
        "missing": missing,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    if not project_root.is_dir():
        report = {"status": "BLOCKED", "error": "project root does not exist"}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    tools = {
        "codex": run_version(["codex", "--version"]),
        "node": run_version(["node", "--version"]),
        "npm": run_version(["npm", "--version"]),
        "npx": run_version(["npx", "--version"]),
    }
    mcp_configs = [
        inspect_mcp_config(project_root / ".codex" / "config.toml"),
        inspect_mcp_config(Path.home() / ".codex" / "config.toml"),
    ]
    playwright_configured = any(item["playwright_section"] for item in mcp_configs)
    extension_configured = any(item["extension_flag"] for item in mcp_configs)
    locations = skill_locations(project_root)
    skill_found = any(item["exists"] for item in locations)
    continuity = inspect_continuity(project_root)
    missing_core = [name for name in ("codex", "node") if not tools[name]["found"]]
    if missing_core:
        status = "BLOCKED"
    elif not playwright_configured or not skill_found:
        status = "PARTIAL"
    else:
        status = "PASS"

    report = {
        "schema_version": "1.0",
        "skill": SKILL_ID,
        "status": status,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "tools": tools,
        "skill_locations": locations,
        "project_continuity": continuity,
        "mcp_configs": mcp_configs,
        "playwright_extension": extension_configured,
        "browser_extension": "UNKNOWN: verify manually in Chrome or Edge",
        "limitations": [
            "This check does not launch Playwright or prove browser extension connectivity.",
            "It does not inspect cookies, tokens, browser profiles, or account identity.",
            "A configured MCP server can still fail at runtime; perform one read-only tab call.",
            "Project continuity checks file presence only; read the memory files and verify relevant raw evidence.",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
