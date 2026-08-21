# R470 patch-series decision record

## Decision

openCUDA will maintain a reproducible NVIDIA R470 Linux kernel-compatibility series as an operational dependency of the Kepler legacy backend.

The series will:

- pin NVIDIA driver version 470.256.02;
- verify the NVIDIA runfile by a recorded upstream SHA-512;
- pin an exact third-party compatibility-patch commit rather than tracking a moving branch;
- record the canonical patch order in `patches/nvidia-r470/SERIES`;
- fetch third-party patches at build time when redistribution rights are not established;
- keep openCUDA-authored patches in a separate `local/` layer;
- isolate unreleased/untested patches in `staging/`;
- separate compile success from K80 hardware-validation status;
- prohibit changes whose purpose is to falsify compute capability or hardware identity.

## Rationale

The Linux PCI subsystem can enumerate the Cubix-attached Tesla K80 devices without a Cubix-specific Linux bus driver, but Kepler CUDA execution depends on NVIDIA's legacy R470 kernel modules. Current Linux kernels continue to change internal APIs after NVIDIA ended normal R470 maintenance. A controlled compatibility layer is therefore needed if openCUDA is to retain the option of running the K80 backend on maintained Linux kernels.

## Alternatives considered

### Freeze the entire system indefinitely

Rejected as the only strategy. A pinned reference kernel remains useful, but indefinite system freeze accumulates unrelated security and maintenance debt.

### Track community DKMS packages without pinning

Rejected. A moving package/branch makes an experimental compatibility stack difficult to reproduce and audit.

### Vendor all third-party patch bodies immediately

Deferred. The selected community repository does not expose a repository-level redistribution license at the pinned commit. openCUDA therefore records provenance and fetches the exact pinned inputs until redistribution rights are clear.

### Replace R470 immediately with Nouveau

Not equivalent. Nouveau is important as a future open-source backend research path but does not provide the NVIDIA CUDA ABI/runtime stack required by the current legacy-CUDA execution strategy.

### Run R470 only inside a VM

Retained as a containment option. VFIO may eventually allow a current host kernel while the guest uses a conservative R470-compatible kernel, subject to IOMMU grouping and P2P/topology validation.

## Consequences

The project gains a reproducible maintenance mechanism but also accepts responsibility for testing kernel-interface patches on real K80 hardware. Successful compilation alone is never a compatibility guarantee.
