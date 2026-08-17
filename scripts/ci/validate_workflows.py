#!/usr/bin/env python3
"""Static security and runtime-support checks for GitHub Actions workflows."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_ACTION_OWNERS = {"actions"}
MINIMUM_ACTION_MAJOR = {
    "actions/checkout": 5,
    "actions/github-script": 8,
    "actions/setup-python": 6,
}
UNTRUSTED_EXPRESSIONS = (
    "github.event.issue.body",
    "github.event.issue.title",
    "github.event.comment.body",
    "github.event.discussion.body",
    "github.event.discussion.title",
    "github.event.pull_request.body",
    "github.event.pull_request.title",
    "github.event.review.body",
)


def load_yaml(path: Path) -> dict[Any, Any]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    return document if isinstance(document, dict) else {}


def _trigger(document: dict[Any, Any]) -> Any:
    return document.get("on", document.get(True))


def _iter_steps(document: dict[Any, Any]):
    for job_name, job in document.get("jobs", {}).items():
        if not isinstance(job, dict):
            continue
        for index, step in enumerate(job.get("steps", [])):
            if isinstance(step, dict):
                yield job_name, index, step


def _action_major(ref: str) -> int | None:
    match = re.fullmatch(r"v(\d+)(?:\.\d+(?:\.\d+)?)?", ref)
    return int(match.group(1)) if match else None


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    document = load_yaml(path)
    trigger = _trigger(document)
    if isinstance(trigger, dict) and "pull_request_target" in trigger:
        errors.append(f"{path}: pull_request_target is prohibited")
    if trigger == "pull_request_target":
        errors.append(f"{path}: pull_request_target is prohibited")

    permissions = document.get("permissions")
    if permissions is None:
        errors.append(f"{path}: top-level permissions must be explicit")
    if permissions == "write-all":
        errors.append(f"{path}: permissions: write-all is prohibited")

    for job_name, index, step in _iter_steps(document):
        uses = step.get("uses")
        if isinstance(uses, str) and not uses.startswith("./"):
            if "@" not in uses:
                errors.append(
                    f"{path}:{job_name}[{index}]: action must have an explicit version"
                )
            else:
                action, ref = uses.rsplit("@", 1)
                owner = action.split("/", 1)[0]
                if owner not in ALLOWED_ACTION_OWNERS:
                    errors.append(
                        f"{path}:{job_name}[{index}]: action owner {owner!r} "
                        "is not allowlisted"
                    )
                version_or_sha = re.fullmatch(
                    r"(?:v\d+(?:\.\d+(?:\.\d+)?)?|[0-9a-f]{40})",
                    ref,
                )
                if not version_or_sha:
                    errors.append(
                        f"{path}:{job_name}[{index}]: action ref {ref!r} must be "
                        "a version tag or full SHA"
                    )
                minimum_major = MINIMUM_ACTION_MAJOR.get(action)
                major = _action_major(ref)
                if minimum_major is not None and major is not None and major < minimum_major:
                    errors.append(
                        f"{path}:{job_name}[{index}]: {action}@{ref} uses an obsolete "
                        f"runtime; require v{minimum_major}+ or a reviewed full-SHA pin"
                    )

        run = step.get("run")
        if isinstance(run, str):
            lowered = run.casefold()
            if re.search(r"(?:curl|wget)[^\n|]*\|\s*(?:bash|sh)\b", lowered):
                errors.append(
                    f"{path}:{job_name}[{index}]: pipe-to-shell download is prohibited"
                )
            for expression in UNTRUSTED_EXPRESSIONS:
                spaced = "${{ " + expression
                compact = "${{" + expression
                if spaced in run or compact in run:
                    errors.append(
                        f"{path}:{job_name}[{index}]: untrusted event text must not "
                        f"be interpolated directly into shell code ({expression})"
                    )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    errors: list[str] = []
    for path in sorted((args.root / ".github" / "workflows").glob("*.yml")):
        errors.extend(validate(path))
    for error in errors:
        print(error)
    print(f"workflow-policy: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
