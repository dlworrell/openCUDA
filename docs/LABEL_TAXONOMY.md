# openCUDA Label Taxonomy

This document defines the current repository label taxonomy derived from the project's architecture, compatibility policy, development environment, reference platform, founding discussion, and staged roadmap.

GitHub labels are flat. openCUDA therefore uses a two-level naming convention:

- a **family label** such as `architectural` identifies the broad concern;
- one or more **qualified labels** such as `architectural:stable-abi` identify the specific concern.

For issues and pull requests, apply the family label whenever a qualified label from that family is used. Qualified labels may be combined across families when work is cross-cutting.

The standard GitHub labels (`bug`, `enhancement`, `documentation`, `question`, `good first issue`, `help wanted`, `duplicate`, `invalid`, and `wontfix`) remain orthogonal type/community/state labels and are not replaced by this taxonomy.

## Operational

Use `operational` for repository operation, builds, CI, deployment of the development environment, diagnostics, security, release mechanics, and measured performance of the working system.

| Label | Scope |
|---|---|
| `operational:build` | Native/Python build execution, build failures, build reproducibility. |
| `operational:ci` | Portable GitHub Actions CI and required quality gates. |
| `operational:hardware-ci` | Self-hosted Kepler/K80 hardware-in-the-loop CI. |
| `operational:diagnostics` | `opencuda doctor`, host capture, topology collection, support bundles. |
| `operational:benchmarking` | Repeatable bandwidth, latency, numerical, and throughput benchmarks. |
| `operational:performance` | Performance regressions, tuning, throughput, utilization, and bottlenecks. |
| `operational:security` | Legacy-driver risk, isolation, dependency security, and security policy. |
| `operational:packaging` | Python/native packaging, install layout, distributable artifacts. |
| `operational:release` | Versioning, release candidates, release notes, and published releases. |
| `operational:observability` | ECC telemetry, health counters, logging, metrics, and runtime visibility. |

## Architectural

Use `architectural` when work changes component boundaries, public interfaces, process isolation, execution policy, memory model, topology model, or major internal abstractions.

| Label | Scope |
|---|---|
| `architectural:portable-core` | CUDA-independent C17 core runtime. |
| `architectural:stable-abi` | Public C ABI, handles, status model, and ABI-versioning rules. |
| `architectural:cpp-layer` | C++20 convenience/RAII layer above the C ABI. |
| `architectural:legacy-backend` | Contained CUDA 11.x legacy execution backend. |
| `architectural:capability-policy` | Native/lowerable/fallback/unsupported capability decisions. |
| `architectural:topology` | PCIe, NUMA, GPU, switch-fabric, and affinity data model. |
| `architectural:scheduler` | Work placement, queues, NUMA affinity, and multi-GPU scheduling. |
| `architectural:transport` | Daemon control protocol, Unix-domain sockets/named pipes, shared memory. |
| `architectural:memory` | Opaque memory handles, pinned staging, residency, allocation policy. |
| `architectural:streams-events` | Project-owned stream/event abstractions and synchronization semantics. |
| `architectural:multi-device` | Logical arrays, tiling, P2P planning, and distributed-memory truth. |
| `architectural:compiler-ir` | Versioned operation IR and compiler/lowering interfaces. |
| `architectural:frontends` | Public language/framework front-end architecture and binding boundaries. |

## Compatibility

Use `compatibility` for support boundaries, legacy-toolchain containment, operation translation, fallback policy, and generation-specific behavior.

| Label | Scope |
|---|---|
| `compatibility:kepler` | NVIDIA Kepler-generation behavior and support. |
| `compatibility:sm37` | Compute capability 3.7 target behavior. |
| `compatibility:cuda11` | CUDA 11.x legacy toolkit/runtime compatibility boundary. |
| `compatibility:r470` | R470 legacy driver branch assumptions and validation. |
| `compatibility:native` | Operation executes natively on the target backend. |
| `compatibility:lowering` | Modern operation is rewritten to older supported primitives. |
| `compatibility:substitution` | Project-owned or legacy-library replacement implementation. |
| `compatibility:cpu-fallback` | Correctness-preserving CPU fallback behavior and policy. |
| `compatibility:unsupported` | Explicitly unrepresentable or intentionally rejected capabilities. |
| `compatibility:legacy-library` | cuBLAS/cuFFT/cuRAND/sparse legacy-library compatibility. |
| `compatibility:source-build` | Source-level kernel rebuilding for legacy architecture targets. |
| `compatibility:future-generation` | Generalization to Maxwell, Pascal, or later retired generations. |
| `compatibility:pytorch` | Framework-level compatibility expectations for a future `kepler:` backend. |

## Developmental

Use `developmental` for implementation language, toolchain, testing, platform/ISA development, developer tooling, and contribution workflow.

| Label | Scope |
|---|---|
| `developmental:c17` | Stable C17 ABI/runtime implementation. |
| `developmental:cpp20` | C++20 implementation and wrappers. |
| `developmental:python` | Python 3.10+ package, orchestration, diagnostics, and tooling. |
| `developmental:assembly` | Narrow assembly primitives with portable fallback. |
| `developmental:cuda-cpp` | Legacy-backend CUDA C++ kernels and host glue. |
| `developmental:cmake` | CMake configuration, presets, feature detection, and build logic. |
| `developmental:testing` | CTest/pytest/unit/integration/correctness tests. |
| `developmental:code-quality` | Compiler warnings, clang-tidy, Ruff, mypy, formatting, static analysis. |
| `developmental:tooling` | Developer scripts and local engineering utilities. |
| `developmental:bindings` | FFI/native extension/buffer-protocol language bindings. |
| `developmental:devcontainer` | Reproducible development container and editor environment. |
| `developmental:linux` | Linux-specific portable or legacy-backend development. |
| `developmental:macos` | macOS-specific portable development. |
| `developmental:windows` | Windows-specific portable/experimental legacy-backend development. |
| `developmental:x86-64` | x86-64 ISA-specific code and testing. |
| `developmental:aarch64` | AArch64/arm64 ISA-specific code and testing. |
| `developmental:documentation` | Engineering documentation maintained with implementation changes. |

## Discussion

Use `discussion` when the primary purpose is technical exploration, design review, research, or a decision that has not yet become committed implementation work.

| Label | Scope |
|---|---|
| `discussion:rfc` | Formal request for comments on a proposed project change. |
| `discussion:design` | Design exploration before an architecture is accepted. |
| `discussion:research` | Feasibility investigation, literature/upstream study, or experiments. |
| `discussion:proposal` | Concrete idea proposed for adoption. |
| `discussion:decision-needed` | Work blocked on an explicit engineering/project decision. |
| `discussion:benchmark-analysis` | Interpretation of measured performance/topology data. |
| `discussion:upstream` | Implications of NVIDIA, PyTorch, compiler, OS, or related upstream changes. |
| `discussion:question` | Open technical question not yet classified as a defect or feature. |

## Reference

Use `reference` when an issue or PR records, validates, or materially depends on reference hardware, topology, upstream specifications, or authoritative implementation examples.

| Label | Scope |
|---|---|
| `reference:dl380p-gen8` | HP ProLiant DL380p Gen8 reference host. |
| `reference:cubix` | CUBIX host interface, enclosure, or PCIe switch fabric. |
| `reference:tesla-k80` | Tesla K80 board-level properties and behavior. |
| `reference:gk210` | Individual GK210 GPU/device properties and behavior. |
| `reference:numa` | NUMA ownership, CPU affinity, memory locality, and QPI path. |
| `reference:pcie` | PCIe generation, width, root-port, switch hierarchy, and host-link behavior. |
| `reference:p2p` | CUDA peer-access topology, bandwidth, and latency. |
| `reference:ecc` | GPU/system ECC state, counters, and reliability information. |
| `reference:nvidia-cuda` | NVIDIA CUDA documentation, architecture matrix, driver/toolkit behavior. |
| `reference:pytorch-privateuse1` | PyTorch `PrivateUse1` accelerator-extension reference material. |
| `reference:opencore-oclp` | OpenCore/OCLP compatibility methodology used as an architectural analogy. |
| `reference:cpu-baseline` | Deterministic CPU implementations used as numerical correctness references. |

## Roadmap

Use `roadmap` for work explicitly tied to the staged implementation plan. Planned implementation work should normally carry exactly one current phase label unless it intentionally spans a phase boundary.

| Label | Phase |
|---|---|
| `roadmap:phase-0-bootstrap` | Bootstrap: portable build, package skeleton, assembly abstraction, initial CI/docs. |
| `roadmap:phase-1-hardware-discovery` | Device ABI, Driver API discovery, UUID/PCI mapping, topology, ECC, P2P. |
| `roadmap:phase-2-execution-service` | Long-lived CUDA 11.x daemon, protocol, shared/pinned memory, handles. |
| `roadmap:phase-3-scheduler` | NUMA-aware scheduling, memory accounting, queues, P2P transfer planning. |
| `roadmap:phase-4-numerical-libraries` | cuBLAS/cuFFT/cuRAND/sparse wrappers and correctness tests. |
| `roadmap:phase-5-compiler-lowering` | Operation IR, `sm_37` build helper, capability DB, lowering/substitution. |
| `roadmap:phase-6-python-scientific` | Python FFI/native extension, NumPy, async API, safe buffer interoperability. |
| `roadmap:phase-7-pytorch-kepler` | PyTorch `PrivateUse1`/`kepler:` research and operator integration. |
| `roadmap:phase-8-general-framework` | Architecture profiles beyond Kepler and per-generation regression matrix. |

## Label application rules

1. **Type first.** Use a standard GitHub type label such as `bug`, `enhancement`, `documentation`, or `question` when appropriate.
2. **Family plus qualifier.** If `architectural:topology` applies, also apply `architectural`.
3. **Roadmap is scheduling, not ownership.** A Phase 1 topology issue can also be `architectural:topology`, `reference:pcie`, and `developmental:c17`.
4. **Compatibility describes behavior.** Do not use `compatibility:unsupported` merely because work is unfinished; it means the requested capability cannot currently be represented correctly by policy/design.
5. **Discussion is pre-commitment.** Remove or supplement discussion labels once a decision becomes an implementation issue.
6. **Reference is evidence/context.** Hardware/upstream labels identify what evidence or platform a work item depends on; they do not imply implementation ownership.
7. **Do not invent one-off labels.** Add a new qualified label only when at least one current or planned project concern cannot be represented by this taxonomy.
8. **Keep labels evidence-based.** Update this document when architecture, supported hosts, compatibility boundaries, or roadmap phases change.

## Examples

A Phase 1 issue to read K80 UUIDs and PCI IDs through the CUDA Driver API should use:

`enhancement`, `roadmap`, `roadmap:phase-1-hardware-discovery`, `architectural`, `architectural:topology`, `compatibility`, `compatibility:kepler`, `compatibility:sm37`, `reference`, `reference:tesla-k80`, `reference:pcie`, `developmental`, `developmental:c17`, `developmental:cuda-cpp`.

A future PyTorch matrix-multiply integration backed by legacy cuBLAS should use:

`enhancement`, `roadmap`, `roadmap:phase-7-pytorch-kepler`, `architectural`, `architectural:frontends`, `compatibility`, `compatibility:pytorch`, `compatibility:legacy-library`, `developmental`, `developmental:python`, `reference`, `reference:pytorch-privateuse1`.
