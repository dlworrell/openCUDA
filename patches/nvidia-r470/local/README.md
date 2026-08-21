# openCUDA-local R470 patches

This directory is reserved for openCUDA-authored changes applied **after** the pinned upstream compatibility series.

Requirements for every patch:

- identify the kernel/API break being fixed;
- include authorship and `Signed-off-by` metadata;
- state the minimum/maximum tested kernel versions;
- include or reference a regression test/build log;
- avoid compute-capability spoofing or GPU identity changes;
- prefer submission upstream when the change is generally useful.

A local patch is not considered supported merely because it compiles. Promotion to the reference execution image requires K80 hardware validation.
