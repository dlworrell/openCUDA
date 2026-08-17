from __future__ import annotations

from pathlib import Path

import pytest
from scripts.ci.content_policy import load_policy, scan_text
from scripts.ci.moderate_event import extract

ROOT = Path(__file__).resolve().parents[2]


def _payload(kind: str, body: str) -> dict[str, object]:
    user = {"login": "contributor"}
    discussion = {
        "number": 7,
        "node_id": "D_test",
        "title": "Discussion title",
        "body": body,
        "html_url": "https://example.invalid/discussions/7",
        "user": user,
    }
    issue = {
        "number": 8,
        "node_id": "I_test",
        "title": "Issue title",
        "body": body,
        "html_url": "https://example.invalid/issues/8",
        "user": user,
    }
    pull_request = {
        "number": 9,
        "node_id": "PR_test",
        "title": "Pull request title",
        "body": body,
        "html_url": "https://example.invalid/pull/9",
        "user": user,
    }
    if kind == "discussion":
        return {"discussion": discussion}
    if kind == "discussion_comment":
        return {
            "discussion": discussion,
            "comment": {
                "id": 70,
                "node_id": "DC_test",
                "body": body,
                "html_url": "https://example.invalid/discussions/7#comment-70",
                "user": user,
            },
        }
    if kind == "issues":
        return {"issue": issue}
    if kind == "issue_comment":
        return {
            "issue": issue,
            "comment": {
                "id": 80,
                "body": body,
                "html_url": "https://example.invalid/issues/8#comment-80",
                "user": user,
            },
        }
    if kind == "pull_request":
        return {"pull_request": pull_request}
    if kind == "pull_request_review":
        return {
            "pull_request": pull_request,
            "review": {
                "id": 90,
                "body": body,
                "html_url": "https://example.invalid/pull/9#review-90",
                "user": user,
            },
        }
    if kind == "pull_request_review_comment":
        return {
            "pull_request": pull_request,
            "comment": {
                "id": 91,
                "body": body,
                "html_url": "https://example.invalid/pull/9#comment-91",
                "user": user,
            },
        }
    raise AssertionError(kind)


@pytest.mark.parametrize(
    "event_name",
    [
        "discussion",
        "discussion_comment",
        "issues",
        "issue_comment",
        "pull_request",
        "pull_request_review",
        "pull_request_review_comment",
    ],
)
def test_all_supported_event_adapters_extract_actor_url_and_text(event_name: str) -> None:
    text, meta = extract(_payload(event_name, "ordinary technical content"), event_name)
    assert "ordinary technical content" in text
    assert meta["actor"] == "contributor"
    assert str(meta["url"]).startswith("https://example.invalid/")
    assert meta["parent_number"] in {7, 8, 9}


def test_event_adapter_output_reaches_blocking_policy() -> None:
    policy = load_policy(ROOT / "config" / "content-policy.json")
    block_category = next(item for item in policy["categories"] if item["severity"] == "block")
    configured_term = block_category["terms"][0]
    text, meta = extract(_payload("discussion", configured_term), "discussion")
    findings = scan_text(text, policy, source=str(meta["source_key"]), include_media=True)
    assert any(item.severity == "block" for item in findings)


def test_unsupported_event_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported event"):
        extract({}, "workflow_run")
