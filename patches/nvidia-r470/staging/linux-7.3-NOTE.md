# Linux 7.3 compatibility note

The pinned upstream series includes `nvidia-470xx-fix-linux-7.3.patch` authored against Linux 7.3-rc1.

One notable change is the removal/disablement of the legacy NVIDIA ACPI video-driver path on Linux 7.3+, because the kernel replacement API uses GPL-only symbols. The upstream patch states that this affects laptop hotkey handling rather than the core GPU execution path.

For the openCUDA reference platform (server-class Tesla K80 compute devices behind a Cubix PCIe expansion chassis), this is expected to be irrelevant to normal compute operation, but it must still be treated as an experimental kernel-line behavioral difference until hardware validation confirms initialization and compute behavior.

Do not promote Linux 7.3 to a reference execution kernel based on compilation alone.
