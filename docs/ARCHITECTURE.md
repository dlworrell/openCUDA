# openCUDA Architecture

## Principle

openCUDA separates **modern application compatibility** from **legacy GPU execution**. The legacy CUDA runtime is an implementation detail behind a stable project-owned ABI.

```text
Modern application / framework
C / C++ / Python / future PyTorch PrivateUse1
                 |
                 v
          openCUDA front ends
                 |
          stable C ABI / IR
                 |
       capability + policy layer
          /       |        \
     native    lowerable   unsupported
       |           |            |
       v           v            v
 legacy CUDA   replacement   explicit error
 backend       implementation / CPU fallback
       |
 CUDA 11.x runtime + driver API
       |
   sm_37 device code
       |
 Kepler GPUs / Tesla K80
```

## Layers

### 1. Portable core

The C17 library owns the ABI, status codes, capability vocabulary, handles, and eventually memory/stream/job descriptors. It must build without CUDA installed.

### 2. C++ convenience layer

C++20 wrappers provide RAII and richer data structures without changing the stable C ABI.

### 3. Assembly primitives

Small architecture-specific primitives are permitted where they provide a measurable benefit or expose required low-level behavior. Assembly is isolated by OS and ISA and always has a portable C fallback.

Initial primitive: `opencuda_asm_cpu_relax()`.

### 4. Legacy CUDA backend

The first backend targets CUDA 11.x and `sm_37`. It is compiled only when `OPENCUDA_ENABLE_LEGACY_CUDA=ON`.

The backend must never expose raw CUDA pointers or CUDA runtime objects through the public ABI. Doing so would couple modern clients to the legacy runtime and defeat isolation.

### 5. Capability/lowering layer

Every requested operation should eventually be classified as one of:

- **native** — execute directly on the legacy backend;
- **lowerable** — rewrite to supported operations or a replacement kernel;
- **fallback** — execute on another backend such as CPU when correctness is preserved;
- **unsupported** — reject explicitly.

Correctness takes precedence over pretending that old hardware implements features it does not have.

### 6. Scheduler and topology manager

The scheduler will model:

- NUMA locality;
- PCIe host-link ownership;
- PCIe switch hierarchy;
- per-GPU memory capacity;
- P2P availability and measured bandwidth;
- host-to-device bandwidth;
- current memory pressure and work queue depth.

Eight 12-GB devices remain eight physical memory domains. A future logical array abstraction may tile work across them, but must not report a false 96-GB single-GPU address space.

## Process boundary

The long-term design supports a legacy execution daemon:

```text
modern process
   |
Unix domain socket / named pipe for control
shared memory for bulk host data
   |
legacy execution service
   |
CUDA 11.x
```

This process boundary permits the client to use a contemporary compiler, Python, and framework stack while the service remains pinned to the final toolchain supporting the target GPU.

## PyTorch direction

PyTorch documents `PrivateUse1` for out-of-tree accelerator integration. A later `torch-opencuda` package can investigate exposing devices such as:

```python
x = torch.ones((1024, 1024), device="kepler:0")
```

That requires operator registration, storage/device guards, generators, stream/event behavior, serialization, and explicit fallback policy. It is a later milestone, not part of the bootstrap runtime.
