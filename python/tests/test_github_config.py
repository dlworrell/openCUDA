from __future__ import annotations

from pathlib import Path

from scripts.ci.validate_github_config import validate as validate_github_config
from scripts.ci.validate_workflows import validate as validate_workflow

ROOT = Path(__file__).resolve().parents[2]


def test_github_forms_and_routing_contracts() -> None:
    assert validate_github_config(ROOT) == []


def test_all_workflows_meet_static_security_policy() -> None:
    errors: list[str] = []
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        errors.extend(validate_workflow(path))
    assert errors == []
