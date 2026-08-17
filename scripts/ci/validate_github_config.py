#!/usr/bin/env python3
"""Validate openCUDA Issue/Discussion forms and routing configuration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
VALID_BODY_TYPES = {"markdown", "input", "textarea", "dropdown", "checkboxes"}


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _workflow_on(document: dict[Any, Any]) -> Any:
    return document.get("on", document.get(True))


def validate_form(path: Path, discussion: bool = False) -> list[str]:
    errors: list[str] = []
    document = load_yaml(path)
    if not isinstance(document, dict):
        return [f"{path}: form must be a mapping"]

    required_keys = ("title", "body") if discussion else ("name", "description", "body")
    for key in required_keys:
        if key not in document:
            errors.append(f"{path}: missing top-level {key}")

    if discussion:
        title = document.get("title")
        if not isinstance(title, str):
            errors.append(f"{path}: top-level title must be a string")
        labels = document.get("labels", [])
        if labels is not None and not isinstance(labels, list):
            errors.append(f"{path}: top-level labels must be a list")

    body = document.get("body", [])
    if not isinstance(body, list) or not body:
        errors.append(f"{path}: body must be a non-empty list")
        return errors
    ids: set[str] = set()
    for index, item in enumerate(body):
        if not isinstance(item, dict):
            errors.append(f"{path}: body[{index}] must be a mapping")
            continue
        item_type = item.get("type")
        if item_type not in VALID_BODY_TYPES:
            errors.append(f"{path}: body[{index}] invalid type {item_type!r}")
            continue
        if item_type == "markdown":
            if not isinstance(item.get("attributes", {}).get("value"), str):
                errors.append(f"{path}: markdown item {index} needs attributes.value")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"{path}: body[{index}] needs an id")
        elif item_id in ids:
            errors.append(f"{path}: duplicate id {item_id}")
        else:
            ids.add(item_id)
        attributes = item.get("attributes")
        if not isinstance(attributes, dict) or not attributes.get("label"):
            errors.append(f"{path}: body[{index}] needs attributes.label")
        if item_type == "dropdown" and not attributes.get("options"):
            errors.append(f"{path}: dropdown {item_id or index} needs options")
        if item_type == "checkboxes" and not attributes.get("options"):
            errors.append(f"{path}: checkboxes {item_id or index} needs options")
    return errors


def collect_documented_labels(root: Path) -> set[str]:
    text = "\n".join(
        (root / path).read_text(encoding="utf-8")
        for path in (
            "docs/LABEL_TAXONOMY.md",
            "docs/GOVERNANCE_TAXONOMY.md",
        )
    )
    prefixes = (
        "operational",
        "architectural",
        "compatibility",
        "developmental",
        "discussion",
        "reference",
        "roadmap",
        "role",
        "access",
    )
    labels: set[str] = set()
    for token in text.split("`"):
        token = token.strip()
        if token and " " not in token and any(token.startswith(prefix) for prefix in prefixes):
            labels.add(token)
    return labels


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    issue_dir = root / ".github" / "ISSUE_TEMPLATE"
    discussion_dir = root / ".github" / "DISCUSSION_TEMPLATE"

    config = load_yaml(issue_dir / "config.yml")
    if config.get("blank_issues_enabled") is not False:
        errors.append(
            ".github/ISSUE_TEMPLATE/config.yml: blank_issues_enabled must be false"
        )
    if not config.get("contact_links"):
        errors.append(
            ".github/ISSUE_TEMPLATE/config.yml: contact_links must route exploratory work"
        )

    for path in sorted(issue_dir.glob("*.yml")):
        if path.name != "config.yml":
            errors.extend(validate_form(path))

    category_path = root / "config" / "discussion-categories.json"
    category_contract = json.loads(category_path.read_text(encoding="utf-8"))
    expected_forms = {
        item["form"] for item in category_contract["categories"] if item.get("form")
    }
    actual_forms = {path.name for path in discussion_dir.glob("*.yml")}
    if expected_forms != actual_forms:
        errors.append(
            "Discussion forms mismatch: "
            f"expected={sorted(expected_forms)} actual={sorted(actual_forms)}"
        )
    slugs = [item["slug"] for item in category_contract["categories"]]
    if len(slugs) != len(set(slugs)):
        errors.append("config/discussion-categories.json: duplicate category slug")
    for item in category_contract["categories"]:
        form = item.get("form")
        if item["format"] == "poll" and form is not None:
            errors.append(f"{item['slug']}: poll categories must not declare a form")
        if form:
            if Path(form).stem != item["slug"]:
                errors.append(
                    f"{form}: filename must match category slug {item['slug']}"
                )
            errors.extend(validate_form(discussion_dir / form, discussion=True))

    documented_labels = collect_documented_labels(root)
    routing_path = root / "config" / "issue-routing.json"
    routing = json.loads(routing_path.read_text(encoding="utf-8"))
    for rule in routing.get("rules", []):
        if not rule.get("needle") or not rule.get("labels"):
            errors.append("config/issue-routing.json: every rule needs needle and labels")
        for label in rule.get("labels", []):
            if label not in documented_labels:
                errors.append(f"config/issue-routing.json: undocumented label {label}")

    workflows = root / ".github" / "workflows"
    required_workflows = {
        "ci.yml",
        "issue-routing.yml",
        "bootstrap-discussions.yml",
        "kepler-self-hosted.yml",
        "compliance.yml",
        "content-moderation.yml",
        "repository-audit.yml",
    }
    existing = {path.name for path in workflows.glob("*.yml")}
    missing = required_workflows - existing
    if missing:
        errors.append(f"missing required workflow(s): {sorted(missing)}")

    for path in workflows.glob("*.yml"):
        document = load_yaml(path)
        if not isinstance(document, dict) or _workflow_on(document) is None:
            errors.append(f"{path}: workflow has no trigger")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    errors = validate(args.root.resolve())
    for error in errors:
        print(error)
    print(f"github-config: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
