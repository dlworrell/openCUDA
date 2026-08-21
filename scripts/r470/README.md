# R470 maintenance scripts

These scripts intentionally operate on external inputs in `.cache/r470/` and do not install or load NVIDIA modules automatically.

- `fetch-upstream.sh` downloads NVIDIA 470.256.02, verifies its pinned SHA-512, clones the exact pinned compatibility-patch commit, and materializes the patch files into the local build cache.
- `apply-series.sh` extracts the NVIDIA runfile and applies `patches/nvidia-r470/SERIES` in deterministic order.
- `verify-series.sh` performs repository/provenance checks without downloading or modifying system software.

System installation/loading remains a deliberate operator action. The GitHub Actions workflow only performs the hardware build step when manually dispatched with `hardware_build=true` on the self-hosted Kepler runner.
