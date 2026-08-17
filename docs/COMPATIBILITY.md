# Compatibility Policy

## Hard boundary: Kepler and modern CUDA

NVIDIA's CUDA architecture matrix lists Kepler compute capability 3.5/3.7 as supported through CUDA 11.x, with R470 as the final driver branch. The openCUDA Kepler backend therefore targets the final vendor-supported execution generation rather than attempting to coerce CUDA 12+ into compiling `sm_37`.

Reference: https://docs.nvidia.com/datacenter/tesla/drivers/latest/cuda-toolkit-driver-and-architecture-matrix.html

## What can be bridged

openCUDA can reasonably bridge:

1. Modern host applications to a legacy execution service.
2. Stable project-owned APIs to old CUDA libraries.
3. Source-level kernels that can still be compiled as `sm_37`.
4. Modern operations that can be lowered into Kepler-supported primitives.
5. Library functions that have mathematically equivalent legacy implementations.
6. Unsupported accelerator operations to CPU fallback when correctness is preserved and the user has not disabled fallback.

## What cannot be assumed

openCUDA must not assume that it can:

- execute cubins compiled only for modern GPU architectures;
- JIT arbitrary new PTX backwards to Kepler;
- reproduce tensor cores, BF16/FP8 hardware, or new synchronization semantics by changing a device ID;
- present eight independent K80 GPU memories as one physically coherent 96-GB VRAM space;
- make a legacy driver secure merely by wrapping it.

## OpenCore/OCLP analogy

The project borrows the *method*, not implementation code, from OpenCore/OCLP:

- detect actual hardware;
- restore or substitute only missing functionality;
- avoid broad, unnecessary patching;
- retain native behavior where it exists;
- describe unsupported boundaries explicitly.

OCLP documents injected components, kernel patches, device properties, and on-disk restoration of graphics frameworks/drivers for older hardware. openCUDA applies the same compatibility discipline to a user-space compute stack.

Reference: https://github.com/dortania/OpenCore-Legacy-Patcher/blob/main/docs/PATCHEXPLAIN.md

## Compatibility report

A future `opencuda inspect` command should generate a machine-readable report containing:

- host OS/ISA;
- driver version;
- CUDA toolkit/runtime versions;
- visible GPUs and UUIDs;
- compute capabilities;
- memory per GPU;
- ECC mode and error counters when available;
- PCIe negotiated generation/width;
- NUMA affinity;
- P2P matrix;
- supported openCUDA operations and lowering paths.
