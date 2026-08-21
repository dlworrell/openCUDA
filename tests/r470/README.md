# R470 compatibility tests

This directory documents and will host tests used to promote an NVIDIA R470/kernel combination through the validation ladder in `docs/R470_KERNEL_COMPATIBILITY.md`.

Planned test groups:

- build-only kernel/module matrix;
- module load/unload smoke test;
- K80/GK210 enumeration and identity;
- CUDA Driver API initialization;
- allocation/copy/kernel-launch correctness;
- ECC telemetry;
- Cubix/PCIe topology capture;
- multi-device/P2P capability matrix;
- repeated initialization and teardown.

Hardware tests must record exact kernel, compiler, driver, patch-series commit, CUDA toolkit/runtime, PCI topology, and device identities with the result.
