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


def test_workflow_policy_rejects_obsolete_action_runtime(tmp_path: Path) -> None:
    workflow = tmp_path / "obsolete.yml"
    workflow.write_text(
        """name: obsolete-runtime\n"
        "on: workflow_dispatch\n"
        "permissions:\n"
        "  contents: read\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/github-script@v7\n"
        """,
        encoding="utf-8",
    )
    errors = validate_workflow(workflow)
    assert any("obsolete runtime" in error for error in errors)
