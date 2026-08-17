# Reference Platform: DL380p Gen8 + CUBIX + Tesla K80

## Host

Initial reference node:

- HP ProLiant DL380p Gen8
- 2 × Intel Xeon E5-2620 at 2.0 GHz base clock
- 6 cores / 12 threads per socket; 12 cores / 24 threads total
- 128 GB ECC system memory
- CUBIX host interface attached through a PCIe slot

## Accelerator enclosure

- 4 × Tesla K80 boards
- 2 × GK210 GPUs per board
- 8 CUDA devices total
- 4,992 CUDA cores per K80 board / 19,968 across four boards
- 24 GB GDDR5 per K80 board, physically split 12 GB per GPU
- 96 GB total installed accelerator memory, distributed across eight independent device memory spaces
- approximately 8.73 TFLOPS FP32 peak per K80 board
- approximately 2.91 TFLOPS FP64 peak per K80 board
- approximately 34.92 TFLOPS FP32 and 11.64 TFLOPS FP64 theoretical peak across four boards

## Expected topology

Do not assume the topology from the product labels. Measure it.

```text
socket/NUMA node ?
      |
PCIe x16 host interface
      |
 CUBIX switch fabric
      |
 +----+----+----+----+
 K80  K80  K80  K80
 2GPU 2GPU 2GPU 2GPU
```

The critical questions are:

1. Which CPU socket owns the CUBIX host-interface PCIe root port?
2. At what PCIe generation and width is the host link actually negotiated?
3. How are the K80 onboard switches and CUBIX switches represented in the PCI tree?
4. Which GPU pairs support CUDA peer access?
5. What GPU-to-GPU bandwidth is measured by `p2pBandwidthLatencyTest`?
6. What sustained host-to-device bandwidth is achieved with pinned memory?

## Diagnostic capture

Run:

```bash
./scripts/diagnose_kepler_host.sh | tee opencuda-host-diagnostic.txt
```

or the portable JSON collector:

```bash
python scripts/opencuda_doctor.py > opencuda-doctor.json
```

The Linux diagnostic gathers `lscpu`, `numactl --hardware`, `lspci -tv`, `nvidia-smi -L`, PCI identifiers, and `nvidia-smi topo -m` without changing the system.

## Scheduling model

The preferred workload model is coarse-grained:

```text
host scheduler
  |-- work unit 0 -> GPU0 (12 GB)
  |-- work unit 1 -> GPU1 (12 GB)
  |-- work unit 2 -> GPU2 (12 GB)
  |-- work unit 3 -> GPU3 (12 GB)
  |-- work unit 4 -> GPU4 (12 GB)
  |-- work unit 5 -> GPU5 (12 GB)
  |-- work unit 6 -> GPU6 (12 GB)
  `-- work unit 7 -> GPU7 (12 GB)
```

Keep working sets resident on the GPUs, perform local reductions, and return comparatively small results. Avoid designs that move intermediate data through host RAM on every iteration.

## NUMA policy

After measuring PCIe ownership, allocate pinned staging buffers and primary GPU-service threads from the NUMA node local to the CUBIX host interface whenever possible. Cross-socket QPI traffic should not be the default data path for GPU staging.
