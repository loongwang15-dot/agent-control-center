#!/usr/bin/env python3
"""Validate the portable task/result JSON contract without external packages."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STATUSES = {"PASS", "PARTIAL", "FAIL", "BLOCKED", "NOT_RUN", "UNVERIFIED"}
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def nonempty_string(value, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")


def validate_task(data: dict) -> list[str]:
    errors: list[str] = []
    for field in ("task_id", "goal", "platform", "deliverable"):
        nonempty_string(data.get(field), field, errors)
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    constraints = data.get("constraints")
    if not isinstance(constraints, dict):
        errors.append("constraints must be an object")
    else:
        acceptance = constraints.get("acceptance", [])
        if not isinstance(acceptance, list) or not all(
            isinstance(item, str) and item.strip() for item in acceptance
        ):
            errors.append(
                "constraints.acceptance must be an array of non-empty strings"
            )
        for field in ("allowed_tools", "human_approval"):
            value = constraints.get(field, [])
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                errors.append(
                    f"constraints.{field} must be an array of non-empty strings"
                )
        for field in ("max_retries", "max_cost"):
            if field in constraints and (
                not isinstance(constraints[field], (int, float))
                or isinstance(constraints[field], bool)
                or constraints[field] < 0
            ):
                errors.append(
                    f"constraints.{field} must be a non-negative number"
                )
    inputs = data.get("inputs", [])
    if not isinstance(inputs, list):
        errors.append("inputs must be an array")
    else:
        for index, item in enumerate(inputs):
            if not isinstance(item, dict):
                errors.append(f"inputs[{index}] must be an object")
                continue
            nonempty_string(item.get("kind"), f"inputs[{index}].kind", errors)
            nonempty_string(item.get("ref"), f"inputs[{index}].ref", errors)
            if "sha256" in item and (
                not isinstance(item["sha256"], str)
                or not HASH_RE.fullmatch(item["sha256"])
            ):
                errors.append(
                    f"inputs[{index}].sha256 must be 64 hexadecimal characters"
                )
    return errors


def validate_result(data: dict) -> list[str]:
    errors: list[str] = []
    for field in ("task_id", "run_id", "summary", "next_action"):
        nonempty_string(data.get(field), field, errors)
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    if data.get("status") not in STATUSES:
        errors.append(
            "status must be PASS, PARTIAL, FAIL, BLOCKED, NOT_RUN, or UNVERIFIED"
        )
    actions = data.get("actions", [])
    if not isinstance(actions, list):
        errors.append("actions must be an array")
    elif not all(isinstance(item, str) and item.strip() for item in actions):
        errors.append("actions must contain non-empty strings")
    evidence = data.get("evidence", [])
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
    else:
        for index, item in enumerate(evidence):
            if isinstance(item, str):
                if not item.strip():
                    errors.append(f"evidence[{index}] must not be empty")
            elif isinstance(item, dict):
                nonempty_string(item.get("kind"), f"evidence[{index}].kind", errors)
                nonempty_string(item.get("ref"), f"evidence[{index}].ref", errors)
            else:
                errors.append(f"evidence[{index}] must be a string or object")
    artifacts = data.get("artifacts", [])
    if not isinstance(artifacts, list):
        errors.append("artifacts must be an array")
    else:
        for index, artifact in enumerate(artifacts):
            if not isinstance(artifact, dict):
                errors.append(f"artifacts[{index}] must be an object")
                continue
            nonempty_string(
                artifact.get("path"), f"artifacts[{index}].path", errors
            )
            if "sha256" in artifact and (
                not isinstance(artifact["sha256"], str)
                or not HASH_RE.fullmatch(artifact["sha256"])
            ):
                errors.append(
                    f"artifacts[{index}].sha256 must be 64 hexadecimal characters"
                )
    cost = data.get("cost")
    if cost is not None:
        if not isinstance(cost, dict):
            errors.append("cost must be an object when present")
        else:
            for field in ("before", "after", "spent"):
                if field in cost and (
                    not isinstance(cost[field], (int, float))
                    or isinstance(cost[field], bool)
                    or cost[field] < 0
                ):
                    errors.append(f"cost.{field} must be a non-negative number")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("task", "result"), required=True)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        report = {"status": "BLOCKED", "errors": [str(error)]}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1
    if not isinstance(data, dict):
        errors = ["top-level JSON value must be an object"]
    else:
        errors = validate_task(data) if args.kind == "task" else validate_result(data)
    report = {
        "schema_version": "1.0",
        "kind": args.kind,
        "path": str(args.path.resolve()),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
