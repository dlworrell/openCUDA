# R470 patch provenance

This file records provenance and redistribution policy for the third-party inputs used by the openCUDA R470 kernel-compatibility series.

## NVIDIA installer

- Product: NVIDIA Linux x86_64 Display Driver
- Version: 470.256.02
- File: `NVIDIA-Linux-x86_64-470.256.02.run`
- Source: NVIDIA download service, URL recorded in `UPSTREAM`
- Integrity: SHA-512 recorded in `SHA512SUMS`
- Redistribution: not included in this repository; obtain directly from NVIDIA under NVIDIA's terms.

The SHA-512 value used by openCUDA is the value published by the pinned `nvidia-470xx-linux-mainline` download script for this exact NVIDIA runfile.

## Community kernel-compatibility patches

- Repository: `https://github.com/joanbm/nvidia-470xx-linux-mainline.git`
- Pinned commit: `b68e153b018bb0b5cd4cbd72cb66c84e3b7d18e9`
- Commit description at pin: `Graduate patch for Linux 7.3`
- Ordered patch set: see `SERIES`

At the pinned commit, no repository-level license file was found and the README does not assert a redistribution license for the repository as a whole. Accordingly:

- openCUDA does not copy those patch bodies into this repository by default;
- the build tooling clones the exact pinned commit and copies patches into a local build cache;
- openCUDA records patch names and commit provenance so results are reproducible;
- any future vendoring requires a separate licensing/provenance review.

Individual upstream patches retain their original authorship headers. For example, the Linux 7.3 patch identifies Joan Bruguera Micó as author and describes the specific ACPI API compatibility change.

## openCUDA-owned patches

Any patch authored for openCUDA must be placed in `local/`, contain normal patch authorship and `Signed-off-by` metadata, and state an explicit license/provenance compatible with the repository's contribution policy.

Experimental changes remain under `staging/` and are excluded from the production `SERIES` until reviewed.
