#!/usr/bin/env python3
"""Repository-level source, secret, artifact, and ABI compliance checks."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / "config" / "repository-policy.json"


@dataclass(frozen=True)
class Violation:
    rule: str
    path: str
    line: int
    message: str


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _excluded(relative: str, policy: dict[str, Any]) -> bool:
    return any(relative == item or relative.startswith(item) for item in policy.get("exclude_paths", []))


def _source_file(path: Path) -> bool:
    return path.suffix.lower() in {".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".cu", ".cuh"}


def _strip_c_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", text)


def _line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan_repository(root: Path, policy: dict[str, Any]) -> list[Violation]:
    violations: list[Violation] = []
    forbidden_exts = set(policy["forbidden_binary_extensions"])
    text_exts = set(policy["text_extensions"])
    scan_dirs = tuple(policy["scan_directories"])
    max_size = int(policy["max_file_bytes"])

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if _excluded(relative, policy):
            continue

        parts = Path(relative).parts
        if any(part in policy["forbidden_generated_directories"] for part in parts):
            violations.append(Violation("generated-artifact", relative, 1, "generated/cache directory committed"))

        if path.suffix.lower() in forbidden_exts:
            violations.append(Violation("binary-artifact", relative, 1, "compiled/archive artifact must not be committed"))

        size = path.stat().st_size
        if size > max_size:
            violations.append(Violation("file-size", relative, 1, f"file exceeds {max_size} byte repository limit"))

        should_scan_text = path.suffix in text_exts or path.name in {"CMakeLists.txt", "Makefile"}
        if not should_scan_text:
            continue
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            violations.append(Violation("encoding", relative, 1, "text file is not valid UTF-8"))
            continue

        if "\r\n" in text or "\r" in text:
            violations.append(Violation("line-endings", relative, 1, "text files must use LF line endings"))
        if text and not text.endswith("\n"):
            violations.append(Violation("final-newline", relative, text.count("\n") + 1, "text file must end with newline"))
        for index, line_text in enumerate(text.splitlines(), start=1):
            if line_text.rstrip(" \t") != line_text:
                violations.append(Violation("trailing-whitespace", relative, index, "trailing whitespace"))
            if any(unicodedata.category(ch) == "Cf" and ch not in {"\u200c", "\u200d"} for ch in line_text):
                violations.append(Violation("unicode-control", relative, index, "unexpected Unicode format/control character"))

        for secret in policy["secret_patterns"]:
            match = re.search(secret["pattern"], text)
            if match:
                violations.append(Violation(f"secret:{secret['id']}", relative, _line(text, match.start()), "probable secret/private key material"))

        top = parts[0] if parts else ""
        if top in scan_dirs and _source_file(path):
            code = _strip_c_comments(text)
            for name in policy["unsafe_c_apis"]:
                match = re.search(rf"\b{re.escape(name)}\s*\(", code)
                if match:
                    violations.append(Violation(f"unsafe-api:{name}", relative, _line(code, match.start()), f"unsafe C API {name}() is prohibited"))
            for name in policy["discouraged_c_apis"]:
                match = re.search(rf"\b{re.escape(name)}\s*\(", code)
                if match:
                    violations.append(Violation(f"discouraged-api:{name}", relative, _line(code, match.start()), f"legacy bounded string API {name}() requires an explicit reviewed exception"))

        if relative.startswith("include/opencuda/"):
            for type_name in policy["public_abi_forbidden_types"]:
                match = re.search(rf"\b{re.escape(type_name)}\b", text)
                if match:
                    violations.append(Violation("public-abi-cuda-type", relative, _line(text, match.start()), f"raw CUDA type {type_name} leaks into the public ABI"))

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    args = parser.parse_args(argv)
    policy = load_policy(args.policy)
    violations = scan_repository(args.root.resolve(), policy)
    for item in violations:
        print(f"{item.path}:{item.line}: {item.rule}: {item.message}")
    print(f"repository-policy: {len(violations)} violation(s)")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
