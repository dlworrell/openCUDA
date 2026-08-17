from __future__ import annotations

from pathlib import Path

from scripts.ci.repository_policy import load_policy, scan_repository

ROOT = Path(__file__).resolve().parents[2]


def test_clean_source_tree_passes_basic_fixture(tmp_path: Path) -> None:
    policy = load_policy(ROOT / "config" / "repository-policy.json")
    source = tmp_path / "src" / "core"
    source.mkdir(parents=True)
    (source / "safe.c").write_text("int answer(void) { return 42; }\n", encoding="utf-8")
    assert scan_repository(tmp_path, policy) == []


def test_unsafe_c_api_is_rejected(tmp_path: Path) -> None:
    policy = load_policy(ROOT / "config" / "repository-policy.json")
    source = tmp_path / "src"
    source.mkdir()
    api = policy["unsafe_c_apis"][0]
    (source / "bad.c").write_text(f"void f(char *p) {{ {api}(p); }}\n", encoding="utf-8")
    violations = scan_repository(tmp_path, policy)
    assert any(item.rule == f"unsafe-api:{api}" for item in violations)


def test_raw_cuda_type_is_rejected_from_public_abi(tmp_path: Path) -> None:
    policy = load_policy(ROOT / "config" / "repository-policy.json")
    include = tmp_path / "include" / "opencuda"
    include.mkdir(parents=True)
    type_name = policy["public_abi_forbidden_types"][0]
    (include / "bad.h").write_text(f"typedef {type_name} leaked_type;\n", encoding="utf-8")
    violations = scan_repository(tmp_path, policy)
    assert any(item.rule == "public-abi-cuda-type" for item in violations)


def test_private_key_marker_is_rejected(tmp_path: Path) -> None:
    policy = load_policy(ROOT / "config" / "repository-policy.json")
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    marker = "-----BEGIN " + "PRIVATE KEY-----"
    (scripts / "secret.txt").write_text(marker + "\n", encoding="utf-8")
    violations = scan_repository(tmp_path, policy)
    assert any(item.rule.startswith("secret:") for item in violations)
