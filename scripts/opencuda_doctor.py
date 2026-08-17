#!/usr/bin/env python3
"""Collect a non-destructive development and topology diagnostic report."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
from typing import Any


def _run(command: list[str]) -> dict[str, Any]:
    executable = shutil.which(command[0])
    if executable is None:
        return {"available": False, "command": command[0]}

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    return {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    report: dict[str, Any] = {
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "tools": {
            "cmake": _run(["cmake", "--version"]),
            "cc": _run(["cc", "--version"]),
            "cxx": _run(["c++", "--version"]),
            "nvidia_smi": _run(["nvidia-smi", "-L"]),
        },
    }

    if platform.system() == "Linux":
        report["linux_topology"] = {
            "lscpu": _run(["lscpu"]),
            "numactl": _run(["numactl", "--hardware"]),
            "lspci": _run(["lspci", "-tv"]),
            "nvidia_topology": _run(["nvidia-smi", "topo", "-m"]),
        }

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
