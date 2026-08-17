"""openCUDA Python-facing compatibility package."""

from .runtime import Capability, RuntimeInfo, runtime_info

__all__ = ["Capability", "RuntimeInfo", "runtime_info"]
__version__ = "0.1.0"
