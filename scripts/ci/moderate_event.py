#!/usr/bin/env python3
"""Extract untrusted GitHub collaboration text and apply openCUDA content policy safely."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from content_policy import content_hash, load_policy, scan_text, severity_at_least


def _user_login(value: Any) -> str:
    return str(value.get("login", "unknown")) if isinstance(value, dict) else "unknown"


def extract(payload: dict[str, Any], event_name: str) -> tuple[str, dict[str, Any]]:
    if event_name == "discussion":
        item = payload["discussion"]
        text = f"{item.get('title', '')}\n{item.get('body', '')}"
        meta = {
            "source_kind": "discussion",
            "source_key": f"discussion:{item.get('number')}",
            "number": item.get("number"),
            "parent_number": item.get("number"),
            "parent_node_id": item.get("node_id"),
            "url": item.get("html_url"),
            "actor": _user_login(item.get("user")),
        }
    elif event_name == "discussion_comment":
        comment = payload["comment"]
        discussion = payload["discussion"]
        text = str(comment.get("body", ""))
        meta = {
            "source_kind": "discussion_comment",
            "source_key": f"discussion-comment:{comment.get('node_id', comment.get('id'))}",
            "number": comment.get("id"),
            "parent_number": discussion.get("number"),
            "parent_node_id": discussion.get("node_id"),
            "url": comment.get("html_url") or discussion.get("html_url"),
            "actor": _user_login(comment.get("user")),
        }
    elif event_name == "issues":
        item = payload["issue"]
        text = f"{item.get('title', '')}\n{item.get('body', '')}"
        meta = {
            "source_kind": "issue",
            "source_key": f"issue:{item.get('number')}",
            "number": item.get("number"),
            "parent_number": item.get("number"),
            "parent_node_id": item.get("node_id"),
            "url": item.get("html_url"),
            "actor": _user_login(item.get("user")),
        }
    elif event_name == "issue_comment":
        comment = payload["comment"]
        issue = payload["issue"]
        text = str(comment.get("body", ""))
        meta = {
            "source_kind": "issue_comment",
            "source_key": f"issue-comment:{comment.get('id')}",
            "number": comment.get("id"),
            "parent_number": issue.get("number"),
            "parent_node_id": issue.get("node_id"),
            "url": comment.get("html_url"),
            "actor": _user_login(comment.get("user")),
        }
    elif event_name == "pull_request":
        item = payload["pull_request"]
        text = f"{item.get('title', '')}\n{item.get('body', '')}"
        meta = {
            "source_kind": "pull_request",
            "source_key": f"pull-request:{item.get('number')}",
            "number": item.get("number"),
            "parent_number": item.get("number"),
            "parent_node_id": item.get("node_id"),
            "url": item.get("html_url"),
            "actor": _user_login(item.get("user")),
        }
    elif event_name == "pull_request_review_comment":
        comment = payload["comment"]
        pull_request = payload["pull_request"]
        text = str(comment.get("body", ""))
        meta = {
            "source_kind": "pull_request_review_comment",
            "source_key": f"pull-request-review-comment:{comment.get('id')}",
            "number": comment.get("id"),
            "parent_number": pull_request.get("number"),
            "parent_node_id": pull_request.get("node_id"),
            "url": comment.get("html_url"),
            "actor": _user_login(comment.get("user")),
        }
    else:
        raise ValueError(f"unsupported event: {event_name}")
    return text, meta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, type=Path)
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    payload = json.loads(args.event.read_text(encoding="utf-8"))
    text, meta = extract(payload, args.event_name)
    policy = load_policy()
    findings = scan_text(text, policy, source=meta["source_key"], include_media=True)
    meta.update(
        {
            "content_sha256": content_hash(text),
            "findings": [asdict(item) for item in findings],
            "blocking": any(severity_at_least(item.severity, "warn", policy) for item in findings),
            "requires_review": bool(findings),
        }
    )
    args.output.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"moderation: {len(findings)} finding(s); source={meta['source_key']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
