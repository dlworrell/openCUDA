#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' '=== CPU ==='
lscpu || true
printf '\n%s\n' '=== NUMA ==='
numactl --hardware || true
printf '\n%s\n' '=== PCI TREE ==='
lspci -tv || true
printf '\n%s\n' '=== NVIDIA DEVICES ==='
nvidia-smi -L || true
printf '\n%s\n' '=== GPU PCI INFO ==='
nvidia-smi --query-gpu=index,name,uuid,pci.bus_id,memory.total,power.limit --format=csv || true
printf '\n%s\n' '=== NVIDIA TOPOLOGY ==='
nvidia-smi topo -m || true
printf '\n%s\n' '=== NVIDIA DRIVER ==='
nvidia-smi || true
printf '\n%s\n' '=== KERNEL ==='
uname -a
