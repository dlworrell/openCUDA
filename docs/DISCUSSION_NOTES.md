# Founding Design Discussion

This document records the technical reasoning that led to openCUDA. It is a design record, not a claim that every idea below is already implemented.

## 1. Correcting the Tesla K80 performance model

A Tesla K80 board contains two GK210 GPUs. NVIDIA's published board peak is approximately 8.73 TFLOPS FP32 and 2.91 TFLOPS FP64 **per K80 board**, not per individual GK210 GPU.

For four K80 boards:

- 8 physical GPUs;
- 19,968 CUDA cores total;
- 96 GB physically installed GDDR5, distributed as 12 GB per GPU;
- approximately 34.92 TFLOPS FP32 theoretical peak;
- approximately 11.64 TFLOPS FP64 theoretical peak.

The original 69.84-TFLOPS calculation double-counted the two GPUs on each K80 board.

## 2. Reference host and CUBIX topology

The target machine is an HP ProLiant DL380p Gen8 with two six-core Xeon E5-2620 processors, 128 GB ECC RAM, and a CUBIX PCIe expansion path serving four K80 boards.

The CUBIX architecture makes topology awareness important. Four boards can fan out behind a switch fabric while ultimately sharing host-link bandwidth. For arithmetic-intensive workloads this can still be effective if data is copied to GPU memory in large batches, retained there for many kernels, and reduced before results return to the host.

The project therefore treats PCIe and NUMA behavior as first-class scheduling information.

## 3. Preferred workload shape

The K80 array is best viewed as eight independent 12-GB compute workers rather than a single 96-GB GPU. Prime sieves, Monte Carlo work, parameter searches, and other partitionable numerical workloads can divide the problem domain into large work units and allow each device to operate for long periods without host synchronization.

Pinned host memory, asynchronous streams, measured P2P capability, and NUMA-local staging should be used where they materially improve throughput.

## 4. The software-support problem

Kepler compute capability 3.7 is no longer supported by current CUDA toolchains. NVIDIA's architecture matrix identifies CUDA 11.x as the final toolkit family and R470 as the final driver branch for Kepler 3.5/3.7.

The desired outcome is therefore not "make CUDA 13 think a K80 is a new GPU." Modern cubins, PTX, tensor instructions, synchronization semantics, and library assumptions cannot generally be made backward-compatible by spoofing a device identifier.

## 5. Bridge architecture

The proposed bridge keeps a modern application environment above a stable openCUDA API while isolating CUDA 11.x beneath it.

Possible transport for a daemonized backend:

- Unix-domain socket or platform equivalent for control messages;
- shared memory for bulk host data;
- pinned-memory staging on the backend side;
- opaque handles rather than CUDA pointers crossing the boundary.

This allows the host application, Python environment, and framework integration to evolve independently of the frozen Kepler execution stack.

## 6. OpenCore/OCLP analogy

OpenCore and OpenCore Legacy Patcher provide a useful architectural analogy. OCLP does not solve unsupported hardware by fully emulating a new Mac. It detects the real machine, changes presentation or restores only the components required for that hardware, and uses hardware-specific patch sets.

For openCUDA the equivalent policy is:

1. detect real GPU/PCIe/NUMA capabilities;
2. execute natively when Kepler supports the operation;
3. lower modern operations into older primitives when a correct implementation exists;
4. substitute a project-owned or legacy-library implementation where appropriate;
5. fall back to CPU only when correctness is preserved and policy allows it;
6. reject operations that cannot be represented honestly.

## 7. PyTorch possibility

Current PyTorch documents `PrivateUse1` as the supported mechanism for developing out-of-tree accelerator backends. A future openCUDA integration could register a custom backend name such as `kepler` and eventually support expressions like:

```python
x = torch.ones((4096, 4096), device="kepler:0")
```

This would still require openCUDA implementations for allocation, copies, device guards, streams/events, operators, autograd behavior, serialization, and fallback. `PrivateUse1` provides the integration point; it does not automatically make unsupported CUDA operators run on K80s.

## 8. Generalization

The long-term idea is larger than the K80. openCUDA can become a compatibility framework in which each retired GPU generation has:

- a capability profile;
- its final supported toolkit/driver environment;
- a library set;
- a lowering/substitution policy;
- correctness and performance regression tests.

Kepler is the first backend because there is real multi-GPU hardware available to test it.
