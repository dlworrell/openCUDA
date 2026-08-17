# Development Environment

## Toolchain policy

The portable codebase uses:

- C17 for the stable ABI/runtime;
- C++20 for higher-level wrappers;
- Python 3.10+ for orchestration, diagnostics, tooling, and future bindings;
- assembly for small architecture-specific primitives;
- CMake 3.24+ as the authoritative native build system;
- CTest and pytest for tests.

The portable build must not require a CUDA installation.

## Configure and test

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
cmake --preset dev
cmake --build --preset dev
ctest --preset dev
pytest
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

## Kepler backend

On a machine with CUDA 11.x installed:

```bash
cmake --preset kepler-cuda11
cmake --build --preset kepler-cuda11
ctest --preset kepler-cuda11
```

CMake deliberately refuses CUDA 12+ for the Kepler backend because NVIDIA no longer provides `sm_37` support there.

## Assembly

The current CPU-relax primitive demonstrates the OS/ISA split:

- Linux x86-64: GNU assembler syntax via `.S`;
- macOS x86-64: Clang integrated assembler;
- Linux AArch64: GNU/Clang assembler;
- macOS arm64: Clang integrated assembler;
- Windows x86-64: MASM;
- other configurations: portable C fallback.

Assembly should remain small, documented, independently testable, and replaceable by a portable implementation.

## Python quality gates

```bash
python -m ruff check python scripts
python -m mypy python/opencuda
python -m pytest
```

## Native quality gates

CI builds the portable C/C++ project on Linux, macOS, and Windows and executes CTest. Compiler warnings are enabled by default; `OPENCUDA_WARNINGS_AS_ERRORS=ON` can be used for stricter local validation.

## Legacy-GPU CI

Public GitHub-hosted runners do not provide Tesla K80 hardware. The repository therefore separates portable CI from hardware-in-the-loop testing. A later self-hosted runner on the DL380p should be labeled for Kepler/CUDA 11 and run topology, P2P, memory-bandwidth, ECC, and numerical-correctness tests.

## Branching

Development should land through focused pull requests. Architecture changes should update the relevant design document in the same PR as the implementation.
