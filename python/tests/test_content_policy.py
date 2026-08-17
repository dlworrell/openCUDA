from __future__ import annotations

import json
from pathlib import Path

from scripts.ci.content_policy import load_policy, scan_text

ROOT = Path(__file__).resolve().parents[2]


def test_clean_technical_text_passes() -> None:
    policy = load_policy(ROOT / "config" / "content-policy.json")
    findings = scan_text(
        "Kepler sm_37 topology testing uses pinned memory and deterministic CPU baselines.",
        policy,
        include_media=True,
    )
    assert findings == []


def test_every_block_term_is_detected_without_duplicating_fixture_vocabulary() -> None:
    policy = load_policy(ROOT / "config" / "content-policy.json")
    for category in policy["categories"]:
        if category["severity"] != "block":
            continue
        for term in category["terms"]:
            findings = scan_text(f"prefix {term} suffix", policy, include_media=False)
            assert any(item.category == category["id"] and item.severity == "block" for item in findings)


def test_configured_adult_link_rule_is_detected() -> None:
    policy = load_policy(ROOT / "config" / "content-policy.json")
    rule = policy["regex_rules"][0]
    token = "porn" if "porn" in rule["pattern"] else "xxx"
    findings = scan_text(f"https://example-{token}.invalid/resource", policy, include_media=False)
    assert any(item.rule_id == rule["id"] for item in findings)


def test_embedded_media_requires_review() -> None:
    policy = load_policy(ROOT / "config" / "content-policy.json")
    findings = scan_text("![benchmark plot](attachment.png)", policy, include_media=True)
    assert any(item.rule_id == policy["media_review"]["id"] and item.severity == "review" for item in findings)


def test_policy_file_is_valid_json() -> None:
    document = json.loads((ROOT / "config" / "content-policy.json").read_text(encoding="utf-8"))
    assert document["version"] == 1
