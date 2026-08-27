# Bootable DL380p/CUBIX reference-host scan

Issue: #38

## Purpose

The live-USB scanner inventories the HP ProLiant DL380p Gen8, CUBIX Desktop
Elite, CUBIX `400-A07994` host-interface card, NVIDIA Tesla K80 boards, and
other PCIe devices without mounting or modifying the installed operating-system
disks. Known purchase records identify three K80 boards as NVIDIA assembly
`900-22080-6300-000`, an NVIDIA Quadro 6000 used for host display/management,
and an Intel Xeon Phi 5110P. Physical and PCIe evidence remains authoritative.

The scanner saves a sanitized Markdown report and raw test telemetry to a
writable partition labelled `OPENCUDA_DATA`. It can connect through Wi-Fi and
email the resulting archive to the operator's Gmail account. The Gmail address
and app password are requested interactively and are not written to the report
or persistent storage.

## Live environment requirements

The boot environment must provide:

- Bash, GNU coreutils, `sed`, `awk`, `tar`, `gzip`, `curl`, and `util-linux`;
- NetworkManager and `nmcli`;
- firmware for the selected USB Wi-Fi adapter;
- `pciutils`, `usbutils`, `dmidecode`, `lshw`, `numactl`, `ethtool`,
  `lm-sensors`, and `ipmitool`;
- an NVIDIA R470-compatible kernel module and userspace stack;
- a CUDA toolkit capable of compiling `sm_37`, or a precompiled copy of
  `k80_staged_load` placed beside the scanner.

Do not assume that an arbitrary current distribution kernel can load the
legacy R470 driver. The live image must use a kernel/R470 combination validated
by openCUDA's R470 compatibility work.

The DL380p has no assumed Wi-Fi interface. Use a Linux-supported USB Wi-Fi
adapter whose firmware is already included in the live image. Confirm the
adapter on a different Linux system before relying on it at the server.

## USB layout

Use a bootable live-system partition plus a writable partition with filesystem
label `OPENCUDA_DATA`. Install these files in the live root filesystem:

```text
/usr/local/sbin/opencuda_usb_scan.sh
/usr/local/libexec/k80_staged_load.cu
/etc/systemd/system/opencuda-live-scan.service
```

If the CUDA helper is precompiled, install it as:

```text
/usr/local/sbin/k80_staged_load
```

Adjust the scanner and source-file paths so they remain beside one another, or
install both under `/usr/local/sbin`. Enable the service with:

```bash
systemctl enable opencuda-live-scan.service
```

The service occupies virtual console 1 because Wi-Fi and Gmail credentials are
entered interactively.

## Safety boundary

The Tesla K80 uses a passive heatsink and must not be loaded until verified
high-static-pressure airflow is running through the stock shroud. The scanner
requires the exact phrase `VERIFIED-FORCED-AIRFLOW` before compiling or starting
the CUDA workload.

The default sequence is:

1. 10 minutes idle observation;
2. 15 minutes at approximately 25% compute duty;
3. 30 minutes at full compute duty.

The default software abort threshold is 80 degrees Celsius. This is a
conservative qualification threshold, not a change to the K80 firmware limit.
NVIDIA hardware thermal protection must remain enabled. The scanner terminates
the load if telemetry fails or any GPU reaches the software threshold.

Durations and the abort threshold can be changed for development through:

```text
OPENCUDA_ABORT_TEMP_C
OPENCUDA_IDLE_SECONDS
OPENCUDA_PARTIAL_SECONDS
OPENCUDA_FULL_SECONDS
OPENCUDA_MEMORY_MIB
OPENCUDA_EXPECTED_K80_DEVICES
```

Do not raise the temperature threshold merely to obtain a passing report.

The current scanner cannot read the proposed external thermistors or HP fan
tach signals until the RP2040 controller interface exists. Therefore, operator
confirmation is only an interim gate. Unattended loading is not qualified until
fan tach, thermistor plausibility, watchdog, and full-speed fault behavior are
machine-verifiable.

## Device-count interpretation

Each Tesla K80 contains two GK210 devices. Expected logical NVIDIA counts are:

| Installed K80 boards | Logical NVIDIA devices |
|---:|---:|
| 1 | 2 |
| 2 | 4 |
| 4 | 8 |

The scanner displays the detected count and requires the operator to reconcile
it with the physical installation. It does not silently equate a logical device
count with a physical board count.

The initial qualification default is exactly two logical K80 devices—one
physical K80. If more or fewer are detected, inventory continues but loading is
refused. `OPENCUDA_EXPECTED_K80_DEVICES` exists for later explicitly approved
multi-card qualification; it must not be used to bypass the single-card gate
before one-card cooling is validated.

The load helper receives an explicit list of device indexes whose driver-reported
model is `Tesla K80`. It does not load the Quadro 6000 display GPU or any other
CUDA-capable NVIDIA board merely because that device is visible to the driver.

The Xeon Phi 5110P is inventoried through PCIe and kernel records but is never
included in the NVIDIA/CUDA thermal load.

## Gmail delivery

Use a Google app password created for this one-purpose scanner. The scanner
sends from and to the Gmail address entered at runtime over authenticated SMTP
TLS. The app password exists only in temporary memory-backed files and is
deleted immediately after the send attempt.

If the compressed archive exceeds 18 MB, only the sanitized report is emailed.
The complete archive remains on `OPENCUDA_DATA`. Network or authentication
failure never deletes local results.

## Privacy

The scanner suppresses or redacts common serial-number, UUID, asset-tag, MAC,
and GPU-UUID fields. Review the report before attaching it to a public issue.
Because vendor tools can change their output formats, sanitization reduces but
cannot mathematically guarantee the removal of every unique identifier.

The Gmail app password and Wi-Fi secret must never be committed to openCUDA,
placed in the report, or stored in an unencrypted configuration file.

## Result interpretation

`PASS` means the CUDA helper completed all configured stages without crossing
the software temperature limit or losing NVIDIA telemetry. It does not by
itself qualify memory/VRM cooling, external fan fail-safe behavior, or the
four-card Cubix configuration.

`INVENTORY_COMPLETE_LOAD_NOT_QUALIFIED` means the inventory completed but the
load was declined, unavailable, aborted, or failed. The report and event log
identify the reason.
