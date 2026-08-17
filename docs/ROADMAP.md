# Roadmap

## Phase 0 — Bootstrap

- [x] Cross-platform C17/C++20 build.
- [x] Python package skeleton and tests.
- [x] Linux/macOS/Windows assembly abstraction with portable fallback.
- [x] Optional CUDA 11.x `sm_37` compile boundary.
- [x] Cross-platform portable CI.
- [x] Initial compatibility and reference-platform documentation.

## Phase 1 — Hardware discovery

- [ ] Stable device descriptor ABI.
- [ ] CUDA Driver API backend for GPU discovery.
- [ ] GPU UUID and PCI bus identity mapping.
- [ ] NUMA/PCIe topology collector.
- [ ] Negotiated PCIe generation/width capture.
- [ ] ECC state/error telemetry.
- [ ] P2P capability and benchmark matrix.

## Phase 2 — Legacy execution service

- [ ] Long-lived daemon owning CUDA 11.x contexts.
- [ ] Versioned command protocol.
- [ ] Shared-memory bulk transport.
- [ ] Pinned-memory staging pool.
- [ ] Stream/event abstraction.
- [ ] Stable opaque device/memory/job handles.
- [ ] Clean shutdown/recovery semantics.

## Phase 3 — Scheduler

- [ ] NUMA-aware worker placement.
- [ ] Per-GPU memory accounting.
- [ ] Coarse-grained queue across eight K80 devices.
- [ ] P2P-aware transfer planning.
- [ ] Local reduction primitives.
- [ ] Logical multi-device arrays that preserve physical-memory truth.

## Phase 4 — Numerical libraries

- [ ] cuBLAS compatibility wrapper.
- [ ] cuFFT compatibility wrapper.
- [ ] cuRAND compatibility wrapper.
- [ ] sparse-library evaluation.
- [ ] project-owned kernels for operations missing from the legacy libraries.
- [ ] deterministic correctness tests versus CPU reference implementations.

## Phase 5 — Compiler/lowering work

- [ ] Define a small versioned operation IR.
- [ ] Source-level `sm_37` build helper.
- [ ] Capability database.
- [ ] Native/lowerable/fallback/unsupported classification.
- [ ] Replacement-kernel registry.
- [ ] Compatibility reports emitted during build and at runtime.

## Phase 6 — Python and scientific front ends

- [ ] Native Python extension or FFI layer over the C ABI.
- [ ] NumPy interoperability.
- [ ] asynchronous job API.
- [ ] memoryview/buffer-protocol support where safe.

## Phase 7 — PyTorch `kepler:` backend research

- [ ] Minimal `PrivateUse1` registration proof of concept.
- [ ] device guard, storage, stream, event, and generator integration.
- [ ] initial tensor allocation/copy operators.
- [ ] basic elementwise operators.
- [ ] matrix multiplication via legacy cuBLAS.
- [ ] explicit CPU fallback policy.
- [ ] autograd coverage for supported operators.

## Phase 8 — General legacy CUDA framework

- [ ] Abstract architecture profiles beyond Kepler.
- [ ] Maxwell profile.
- [ ] Pascal profile.
- [ ] per-generation toolkit/driver containment.
- [ ] compatibility-matrix generation and automated regression testing.
