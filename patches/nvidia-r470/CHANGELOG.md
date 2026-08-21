# R470 compatibility series changelog

## 2026-08-21 — initial openCUDA series

- pinned NVIDIA driver 470.256.02;
- pinned `joanbm/nvidia-470xx-linux-mainline` at `b68e153b018bb0b5cd4cbd72cb66c84e3b7d18e9`;
- recorded canonical upstream patch order through the Linux 7.3 development-line patch;
- added NVIDIA runfile SHA-512 verification;
- added deterministic fetch/apply/verify tooling;
- added explicit local and staging patch layers;
- added build-only self-hosted K80 CI entry point;
- added validation ladder, kernel matrix, provenance policy, and reference-hardware checklist;
- deliberately did not vendor third-party patch bodies because repository-level redistribution licensing is not asserted at the pinned upstream commit.
