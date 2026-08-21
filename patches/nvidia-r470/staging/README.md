# Experimental R470 patches

This directory contains patches under investigation for unreleased kernels, new compiler/toolchain breakage, or changes not yet proven safe on the openCUDA reference hardware.

`staging/` patches MUST NOT appear in the production `SERIES` file. They may be exercised only by explicitly experimental CI/jobs until they are reviewed, moved to `local/` or superseded by an upstream patch, and validated according to the compatibility tiers in the parent README.
