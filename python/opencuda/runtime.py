"""Portable runtime metadata.

The first Python layer deliberately does not depend on CUDA. Future native bindings
will sit behind this module without forcing modern Python environments to import the
legacy CUDA runtime directly.
"""

from __future__ import annotations

import platform
from dataclasses import dataclass
from enum import Enum


class Capability(str, Enum):
    """High-level capability states used by front ends."""

    NATIVE = "native"
    LOWERABLE = "lowerable"
    FALLBACK = "fallback"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class RuntimeInfo:
    """Host-side runtime description."""

    system: str
    machine: str
    python: str


def runtime_info() -> RuntimeInfo:
    """Return portable host information without probing CUDA."""

    return RuntimeInfo(
        system=platform.system(),
        machine=platform.machine(),
        python=platform.python_version(),
    )
