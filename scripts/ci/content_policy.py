#!/usr/bin/env python3
"""Deterministic, privacy-conscious text moderation for openCUDA collaboration surfaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / "config" / "content-policy.json"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    category: str
    severity: str
    line: int
    source: str


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    table = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})
    return text.translate(table)


def _line_for(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan_text(text: str, policy: dict[str, Any], source: str = "input", include_media: bool = True) -> list[Finding]:
    normalized = normalize_text(text)
    findings: list[Finding] = []

    for category in policy.get("categories", []):
        category_id = str(category["id"])
        severity = str(category["severity"])
        for term in category.get("terms", []):
            normalized_term = normalize_text(str(term))
            pattern = re.compile(rf"(?<![\w]){re.escape(normalized_term)}(?![\w])", re.IGNORECASE)
            match = pattern.search(normalized)
            if match:
                findings.append(Finding(f"{category_id}:term", category_id, severity, _line_for(normalized, match.start()), source))

    for rule in policy.get("regex_rules", []):
        match = re.search(str(rule["pattern"]), normalized, flags=re.IGNORECASE)
        if match:
            findings.append(
                Finding(str(rule["id"]), str(rule["category"]), str(rule["severity"]), _line_for(normalized, match.start()), source)
            )

    media = policy.get("media_review", {})
    if include_media and media.get("enabled", False):
        media_patterns = (
            re.compile(r"!\[[^\]]*\]\([^)]*\)", re.IGNORECASE),
            re.compile(r"<\s*(?:img|video|source)\b", re.IGNORECASE),
        )
        for pattern in media_patterns:
            match = pattern.search(text)
            if match:
                findings.append(
                    Finding(str(media["id"]), "media", str(media["severity"]), _line_for(text, match.start()), source)
                )
                break

    unique: dict[tuple[str, str, str, int, str], Finding] = {}
    for finding in findings:
        unique[(finding.rule_id, finding.category, finding.severity, finding.line, finding.source)] = finding
    return list(unique.values())


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _excluded(path: Path, root: Path, policy: dict[str, Any]) -> bool:
    relative = path.relative_to(root).as_posix()
    return any(relative == item or relative.startswith(item) for item in policy["repository_scan"]["exclude"])


def scan_repository(root: Path, policy: dict[str, Any]) -> list[Finding]:
    extensions = set(policy["repository_scan"]["extensions"])
    findings: list[Finding] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in extensions or _excluded(path, root, policy):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        findings.extend(scan_text(text, policy, path.relative_to(root).as_posix(), include_media=False))
    return findings


def severity_at_least(severity: str, threshold: str, policy: dict[str, Any]) -> bool:
    order = list(policy["severity_order"])
    return order.index(severity) >= order.index(threshold)


def _emit(findings: list[Finding], json_out: Path | None) -> None:
    payload = {"findings": [asdict(item) for item in findings], "count": len(findings)}
    text = json.dumps(payload, indent=2, sort_keys=True)
    if json_out:
        json_out.write_text(text + "\n", encoding="utf-8")
    print(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--text-file", type=Path)
    parser.add_argument("--scan-repository", type=Path)
    parser.add_argument("--source", default="input")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--fail-on", choices=("review", "warn", "block", "never"), default="block")
    parser.add_argument("--no-media-review", action="store_true")
    args = parser.parse_args(argv)

    policy = load_policy(args.policy)
    if args.text_file:
        findings = scan_text(
            args.text_file.read_text(encoding="utf-8"), policy, args.source, include_media=not args.no_media_review
        )
    elif args.scan_repository:
        findings = scan_repository(args.scan_repository.resolve(), policy)
    else:
        parser.error("one of --text-file or --scan-repository is required")

    _emit(findings, args.json_out)
    if args.fail_on == "never":
        return 0
    return 2 if any(severity_at_least(item.severity, args.fail_on, policy) for item in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
