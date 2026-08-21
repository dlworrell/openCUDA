# R470 reference-hardware validation checklist

Use this checklist when promoting a Linux kernel line from build-tested to reference status on the openCUDA Tesla K80/Cubix node.

## Environment capture

- [ ] Record `uname -a`.
- [ ] Record kernel package/build identifier and config hash.
- [ ] Record compiler, linker, make, and binutils versions.
- [ ] Record NVIDIA driver version `470.256.02`.
- [ ] Record pinned R470 patch upstream commit.
- [ ] Record all openCUDA-local patch SHAs.
- [ ] Record CUDA toolkit/runtime versions.

## Module build/load

- [ ] Build `nvidia.ko`.
- [ ] Build `nvidia-modeset.ko` when exposed.
- [ ] Build `nvidia-drm.ko` when exposed.
- [ ] Build `nvidia-uvm.ko`.
- [ ] Build `nvidia-peermem.ko` when exposed.
- [ ] Check `modinfo` for each module.
- [ ] Load required modules without unresolved-symbol or fatal initialization errors.
- [ ] Record kernel taint state and relevant `dmesg` output.

## Hardware discovery

- [ ] Capture `lspci -tv`.
- [ ] Capture relevant `lspci -nnvvv` bridges/switches/GPU functions.
- [ ] Confirm all expected GK210 devices enumerate.
- [ ] Confirm K80/GK210 PCI IDs, UUIDs, and compute capability remain truthful.
- [ ] Record PCIe link generation/width per GPU where exposed.
- [ ] Capture NUMA locality.

## NVIDIA/CUDA smoke tests

- [ ] `nvidia-smi -q` succeeds.
- [ ] CUDA Driver API initialization succeeds.
- [ ] Device count matches physical expectation.
- [ ] Device names/UUIDs/PCI bus IDs match `nvidia-smi` and PCI inventory.
- [ ] Allocate/free device memory on each GPU.
- [ ] Host-to-device and device-to-host copies pass deterministic verification.
- [ ] Compile/load/launch an `sm_37` test kernel on each GPU.
- [ ] Kernel output matches deterministic CPU reference.
- [ ] Stream/event synchronization smoke test passes.

## Multi-device / Cubix topology

- [ ] Query peer-access capability for every ordered GPU pair.
- [ ] Record P2P matrix rather than assuming board-level connectivity.
- [ ] Exercise supported peer copies.
- [ ] Exercise pinned-host staging fallback where P2P is unavailable.
- [ ] Record link bandwidth/latency baselines if benchmark tooling is available.

## Reliability / telemetry

- [ ] Record ECC enablement and counters.
- [ ] Repeat driver initialization and CUDA enumeration at least 10 times.
- [ ] Run a sustained allocation/copy/kernel loop long enough to expose obvious regressions.
- [ ] Check kernel log for AER, Xid, IOMMU, PCIe, UVM, or NVIDIA warnings/errors.
- [ ] Record temperatures/power/clock state where exposed.

## Promotion decision

- [ ] Attach logs/artifacts to the tracking issue or CI run.
- [ ] Update `config/r470-kernel-matrix.json` only after review.
- [ ] Update `docs/R470_KERNEL_COMPATIBILITY.md` with validated limits/caveats.
- [ ] Do not promote on build success alone.
