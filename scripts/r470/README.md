# R470 maintenance scripts

These scripts intentionally operate on external inputs in `.cache/r470/` and do not install or load NVIDIA modules automatically.

- `fetch-upstream.sh` downloads NVIDIA 470.256.02, verifies its pinned SHA-512, clones the exact pinned compatibility-patch commit, and materializes the patch files into the local build cache.
- `apply-series.sh` extracts the NVIDIA runfile and applies `patches/nvidia-r470/SERIES` in deterministic order.
- `verify-series.sh` performs repository/provenance checks without downloading or modifying system software.

System installation/loading remains a deliberate operator action. The public GitHub Actions workflow rejects `hardware_build=true` on a GitHub-hosted runner. Use the [local operator procedure](../../docs/HARDWARE_EXECUTION_SECURITY.md); do not enroll the lab machine as a public-repository runner.
