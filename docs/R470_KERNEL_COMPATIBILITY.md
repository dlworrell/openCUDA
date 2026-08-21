# R470 Linux kernel compatibility

openCUDA treats NVIDIA R470 as a contained legacy execution dependency, not as the project API.

## Why this exists

Tesla K80/GK210 requires the legacy R470 driver family. NVIDIA no longer updates that branch for current Linux kernel APIs, while the Linux PCI subsystem can continue to enumerate the Cubix-attached devices independently. The practical compatibility problem is therefore the NVIDIA kernel interface rather than the Cubix PCIe enclosure itself.

The patch machinery under `patches/nvidia-r470/` preserves a reproducible path for compiling NVIDIA 470.256.02 against later kernels while keeping the proprietary driver outside the openCUDA repository.

## Provenance model

The series pins an exact revision of the community-maintained `joanbm/nvidia-470xx-linux-mainline` patch project rather than following its moving branch. The initial pin is commit `b68e153b018bb0b5cd4cbd72cb66c84e3b7d18e9`, which includes the graduated Linux 7.3 compatibility patch.

The canonical order is recorded in `patches/nvidia-r470/SERIES`. The NVIDIA `.run` payload is downloaded directly from NVIDIA and validated against the project-pinned SHA-256 before extraction.

## Validation ladder

A kernel version progresses through these states:

1. **patch-known** — an attributable patch exists and is included in the ordered series;
2. **applies** — the complete cumulative series applies cleanly to the extracted 470.256.02 kernel-interface source;
3. **build-tested** — all expected NVIDIA kernel modules compile against that kernel/toolchain;
4. **loads** — modules load on a controlled machine without unresolved symbols or fatal initialization errors;
5. **K80-enumerated** — every expected GK210 device appears through `nvidia-smi` and the CUDA Driver API;
6. **compute-validated** — allocation, copy, kernel launch, synchronization, ECC query, and multi-device discovery tests pass;
7. **reference** — the kernel/toolchain combination is approved for the openCUDA reference execution image.

A higher kernel number is not automatically preferable. The reference node should favor a maintained LTS kernel whose R470 behavior has been characterized on the physical K80/Cubix platform.

## Initial target matrix

| Kernel line | Initial openCUDA status | Intended use |
|---|---|---|
| 6.12 LTS | candidate `reference` | conservative execution node baseline |
| 6.18 LTS | `build-tested` target | later LTS migration candidate |
| 7.2 | `build-tested` + hardware research | current-generation compatibility work |
| 7.3 development line | `experimental` | early breakage detection only |

These statuses describe openCUDA validation, not merely upstream patch availability.

## Runtime validation minimum

Before a patched kernel/driver combination reaches `reference`, record at minimum:

- `uname -a` and kernel configuration identity;
- compiler/binutils versions;
- exact R470 patch upstream commit and any local patches;
- successful module build and module metadata;
- module load/unload behavior;
- `nvidia-smi -q` output sufficient to establish all expected K80/GK210 devices;
- CUDA Driver API version/device enumeration;
- per-device allocation and host↔device transfer;
- a deterministic `sm_37` kernel launch with CPU-reference comparison;
- P2P capability matrix across all visible GK210 devices;
- ECC state/error counters;
- PCIe link width/speed and NUMA/topology capture;
- repeated initialization/teardown to expose obvious stability regressions.

## Security and support statement

R470 is a legacy proprietary driver. Kernel compatibility patches do not convert it into a current supported or security-maintained NVIDIA driver. openCUDA must therefore keep the legacy backend isolated, document the precise tested stack, and retain the option to move it behind a dedicated service or VFIO-backed VM if host-kernel evolution makes direct installation undesirable.

## Update procedure

When upstream publishes a new patch:

1. review the upstream commit and patch provenance;
2. update the pinned commit in `UPSTREAM` only on a dedicated branch;
3. update `SERIES` if the canonical order changes;
4. run metadata and application checks;
5. compile against the affected kernel lines;
6. run K80 hardware validation before changing a kernel's support tier;
7. record the evidence in the associated issue/PR.

Do not merge a newer compatibility patch solely because it makes compilation succeed.
