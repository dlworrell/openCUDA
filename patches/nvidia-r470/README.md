# NVIDIA R470 Linux kernel compatibility series

This directory defines openCUDA's auditable compatibility series for NVIDIA's legacy 470.256.02 Linux driver, the final NVIDIA branch supporting Kepler-class GPUs such as Tesla K80.

## Scope

openCUDA does **not** redistribute NVIDIA's proprietary driver payload. The NVIDIA installer remains an external prerequisite obtained from NVIDIA under NVIDIA's terms.

The compatibility series applies source patches only to the kernel-interface portion extracted from `NVIDIA-Linux-x86_64-470.256.02.run`. The series is intended to keep the legacy execution node buildable while openCUDA separately preserves a modern project-owned API and execution-service boundary.

## Upstream baseline

The initial series is derived from and pinned to:

- project: `joanbm/nvidia-470xx-linux-mainline`
- commit: `b68e153b018bb0b5cd4cbd72cb66c84e3b7d18e9`
- upstream commit message: `Graduate patch for Linux 7.3`
- upstream license for the patch project: GPL-2.0
- NVIDIA driver version: `470.256.02`

The pinned upstream series currently carries compatibility changes from Linux 6.10 through the Linux 7.3 development line, including compiler/conftest fixes. openCUDA must never silently follow the upstream default branch; changing the pinned commit requires review and CI evidence.

## Layout

```text
patches/nvidia-r470/
├── README.md                 # policy and maintenance contract
├── SERIES                    # canonical ordered patch list
├── UPSTREAM                  # pinned provenance
├── local/                    # openCUDA-owned patches, if needed
└── staging/                  # experimental patches; never production by default

scripts/r470/
├── fetch-upstream.sh         # obtain/verify NVIDIA + patch source inputs
├── apply-series.sh           # apply canonical series in deterministic order
└── verify-series.sh          # structural/provenance checks
```

The upstream patch files are synchronized from the pinned GPL-2.0 patch repository during the bootstrap phase. openCUDA-owned modifications belong in `local/` and must carry normal patch authorship and Signed-off-by metadata.

## Compatibility tiers

| Tier | Meaning |
|---|---|
| `reference` | Hardware-tested on the openCUDA K80 node and eligible for the supported execution image. |
| `build-tested` | Kernel module compilation is exercised in CI but hardware runtime validation is pending. |
| `experimental` | Patch applies/builds only in development testing; no compatibility claim. |
| `unsupported` | Known not to work or intentionally outside the maintained series. |

Initial policy:

- Linux 6.12 LTS: target `reference` execution kernel after K80 validation.
- Linux 6.18 LTS: `build-tested` until K80 validation.
- Linux 7.2: `build-tested`/hardware-research target.
- Linux 7.3 development line: `experimental` until released and validated.

## Security boundary

Successful compilation is **not** evidence that the proprietary R470 stack meets current kernel security expectations. R470 remains legacy proprietary code and taints the kernel. openCUDA should minimize its privilege/exposure, isolate legacy execution where practical, and treat newer-kernel patches as maintenance rather than security modernization.

## Rules for adding a patch

1. Identify the exact kernel API break and upstream kernel commit when possible.
2. Prefer a minimal kernel-interface adaptation over version-number conditionals.
3. Preserve compatibility with older supported kernels unless a separate series split is justified.
4. Build all five NVIDIA kernel modules where the driver exposes them: `nvidia`, `nvidia-modeset`, `nvidia-drm`, `nvidia-uvm`, and `nvidia-peermem`.
5. Record compiler version, kernel release, patch set, and build log.
6. Hardware promotion requires K80 initialization, `nvidia-smi`, CUDA Driver API enumeration, memory allocation/copy, kernel launch, and multi-GPU discovery tests.
7. Never patch the driver to falsify compute capability or GPU identity.

## Relationship to openCUDA

This series exists to keep the **legacy backend** viable. It does not become the public openCUDA API and does not change the project's compatibility truth model. The long-term design still permits containment in a pinned execution service or VM even if the surrounding host runs a newer Linux kernel.
