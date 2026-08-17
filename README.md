# openCUDA

openCUDA is an experimental compatibility framework for extending the useful life of legacy NVIDIA CUDA hardware behind a modern software-facing interface.

The initial reference target is **NVIDIA Kepler compute capability 3.7**, especially Tesla K80 accelerators. NVIDIA's current architecture matrix lists CUDA 11.x as the final toolkit family for Kepler 3.5/3.7 and R470 as the final driver branch. openCUDA therefore does **not** pretend that a K80 is a newer GPU. Instead, it isolates a legacy CUDA execution backend and exposes a stable, modern-facing API above it.

The design is inspired by the compatibility philosophy used by OpenCore/OpenCore Legacy Patcher: detect the real hardware, patch or translate only what is necessary, preserve native execution where possible, and fail explicitly when a requested capability cannot be reproduced correctly.

## Project goals

- Keep modern host-side C, C++, and Python applications decoupled from the legacy CUDA toolchain.
- Provide a stable C ABI that higher-level language bindings can target.
- Build an optional CUDA 11.x backend targeting `sm_37` for Kepler.
- Treat multi-GPU installations as distributed devices rather than falsely presenting physically separate memory as one monolithic VRAM pool.
- Discover PCIe, NUMA, and GPU topology and use that information for scheduling.
- Minimize CPU/GPU transfers and prefer long-lived device allocations, coarse-grained work units, pinned memory, streams, and peer-to-peer transfers when the topology supports them.
- Provide future front ends for NumPy and PyTorch, including investigation of PyTorch `PrivateUse1` as an out-of-tree `kepler:` accelerator backend.
- Remain useful as a general legacy-CUDA compatibility framework as additional GPU generations age out of current toolchains.

## What openCUDA is not

openCUDA is **not** a CUDA 12/13 binary emulator and does not promise that modern SASS/PTX can execute on Kepler. Newer GPU instructions and memory semantics cannot generally be translated transparently into `sm_37`. Source-level lowering, library substitution, and explicit CPU fallback are the intended compatibility mechanisms.

## Reference platform

The first hardware target is:

- HP ProLiant DL380p Gen8
- 2 × Intel Xeon E5-2620, 6 cores each
- 128 GB ECC system memory
- CUBIX PCIe expansion chassis / host interface
- 4 × NVIDIA Tesla K80 boards
- 8 × GK210 GPUs total
- 12 GB GDDR5 per GPU / 96 GB physically installed across the eight devices
- approximately 34.92 TFLOPS theoretical FP32 peak across four K80 boards
- approximately 11.64 TFLOPS theoretical FP64 peak across four K80 boards

See [`docs/REFERENCE_PLATFORM.md`](docs/REFERENCE_PLATFORM.md) for the topology and operating assumptions.

## Supported development hosts

| Host | Portable core | Python | Assembly | Legacy CUDA backend |
|---|---:|---:|---:|---:|
| Linux x86-64 | Tier 1 | Tier 1 | x86-64 GAS | **Tier 1 reference** |
| Linux AArch64 | Tier 2 | Tier 1 | AArch64 GAS | Experimental/not reference hardware |
| macOS x86-64 | Tier 1 | Tier 1 | x86-64 Clang assembler | No K80 execution backend |
| macOS arm64 | Tier 1 | Tier 1 | AArch64 Clang assembler | No K80 execution backend |
| Windows x86-64 | Tier 1 | Tier 1 | MASM | Experimental; depends on legacy NVIDIA driver availability |

The portable project can be developed and tested without a GPU. The Kepler backend is deliberately isolated behind `OPENCUDA_ENABLE_LEGACY_CUDA`.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate               # Windows: .venv\\Scripts\\activate
python -m pip install -e '.[dev]'

cmake --preset dev
cmake --build --preset dev
ctest --preset dev
pytest
```

For a legacy CUDA build on a Linux K80 host:

```bash
cmake --preset kepler-cuda11
cmake --build --preset kepler-cuda11
ctest --preset kepler-cuda11
```

That preset intentionally fails if CMake discovers CUDA 12 or newer.

## Repository map

```text
include/opencuda/       Stable public C/C++ headers
src/core/               Portable C runtime and ABI
src/cpp/                C++ convenience layer
src/asm/                Architecture/OS assembly primitives
src/legacy_cuda/        Optional CUDA 11.x / sm_37 backend
python/opencuda/        Python package and future bindings
scripts/                Diagnostics and developer tooling
docs/                   Architecture, compatibility, governance, roadmap, discussion record
tests/                  Native tests
.github/workflows/       Cross-platform CI and repository routing automation
.github/ISSUE_TEMPLATE/  Structured issue/work-item intake
.github/DISCUSSION_TEMPLATE/ Structured Discussion category forms
.github/CODEOWNERS       Review ownership/routing baseline
```

## Documentation

- [`docs/DISCUSSION_NOTES.md`](docs/DISCUSSION_NOTES.md) — design discussion that motivated the project
- [`docs/ISSUES_AND_DISCUSSIONS.md`](docs/ISSUES_AND_DISCUSSIONS.md) — Discussion categories/forms, issue intake, promotion, moderation, and routing lifecycle
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — component model and ABI boundaries
- [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md) — compatibility policy and hard architectural limits
- [`docs/REFERENCE_PLATFORM.md`](docs/REFERENCE_PLATFORM.md) — DL380p/CUBIX/K80 reference node
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) — toolchains, build presets, CI, and coding workflow
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — staged implementation plan
- [`docs/LABEL_TAXONOMY.md`](docs/LABEL_TAXONOMY.md) — technical repository label families, qualified labels, and application rules
- [`docs/GOVERNANCE_TAXONOMY.md`](docs/GOVERNANCE_TAXONOMY.md) — role-routing and L0–L7 access/governance labels
- [`GOVERNANCE.md`](GOVERNANCE.md) — administration levels, functional roles, approval matrix, task assignment, merge authority, and escalation
- [`docs/ROLE_ASSIGNMENTS.md`](docs/ROLE_ASSIGNMENTS.md) — authoritative user/team role registry and bootstrap assignments
- [`.github/CODEOWNERS`](.github/CODEOWNERS) — machine-readable review ownership baseline
- [`SECURITY.md`](SECURITY.md) — security and legacy-driver risk policy

## Governance summary

openCUDA separates repository access from project authority. Pull-request review, task assignment, architecture/compatibility approval, documentation approval, security review, releases, hardware validation, and repository administration are delegated as explicit functional roles. Administration levels run from **L0 Observer** through **L7 Project Owner**, with least privilege as the default. See `GOVERNANCE.md` for the binding policy.

## Upstream references

- NVIDIA CUDA Toolkit, Driver, and Architecture Matrix: https://docs.nvidia.com/datacenter/tesla/drivers/latest/cuda-toolkit-driver-and-architecture-matrix.html
- PyTorch PrivateUse1 backend integration: https://docs.pytorch.org/tutorials/advanced/privateuseone.html
- OpenCore Legacy Patcher patch explanation: https://github.com/dortania/OpenCore-Legacy-Patcher/blob/main/docs/PATCHEXPLAIN.md

## Name and affiliation

openCUDA is an independent research/development project. It is not affiliated with or endorsed by NVIDIA Corporation, CUDA, PyTorch, OpenCore, Acidanthera, or Dortania. CUDA is a trademark of NVIDIA Corporation.
