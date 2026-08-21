# HP ProLiant DL380p Gen8 platform preservation

Issue: #36

## Purpose

The HP ProLiant DL380p Gen8 is the openCUDA reference host platform for the Cubix/Tesla K80 system. This document separates three different questions that must not be conflated:

1. what HP/HPE shipped or supported for the DL380p Gen8 platform generally;
2. what operating systems provide native/open-source support for the underlying devices;
3. what hardware and firmware are actually installed in the openCUDA reference server.

The first is a preservation catalogue. The second is an operating-system compatibility map. The third is a measured machine inventory.

## Preservation policy

For each HPE asset, record provenance, version, release date, source URL, retrieval date, applicable hardware, operating-system family, checksum when available, and redistribution status.

Public availability does not imply permission to redistribute proprietary HPE firmware, drivers, utilities, or Service Pack for ProLiant media. Unless redistribution rights are established, openCUDA records URLs, metadata, hashes, document identifiers, and recovery notes rather than committing binary payloads.

Open-source operating-system drivers are referenced to their authoritative source trees and license information.

## Catalogue domains

### Platform firmware

- System ROM / BIOS
- iLO 4
- Smart Array controllers
- SAS/storage expanders
- FlexibleLOM and supported NICs
- optional Fibre Channel, InfiniBand, and SAS HBAs
- other platform-management firmware published for Gen8

### Windows software

- storage and Smart Array drivers
- Ethernet/FlexibleLOM drivers
- chipset/platform components
- management agents
- Smart Storage Administrator / ACU lineage
- iLO management tools
- Smart Update Manager
- Service Pack for ProLiant components
- diagnostics

### Linux software

- HPE management packages and utilities
- Smart Array administration
- iLO utilities
- Smart Update Manager / SPP support
- HPE agents where historically applicable
- mapping of supported devices to upstream Linux drivers and source trees

### BSD operating systems

The preservation effort records native driver support and source-tree locations for FreeBSD, OpenBSD, and NetBSD rather than assuming an HPE-provided BSD driver pack exists.

### Documentation

- QuickSpecs
- maintenance/service guide
- setup/user guides
- ROM/BIOS documentation
- iLO 4 documentation
- Smart Array manuals
- PCIe/riser topology
- memory population rules
- thermal/power specifications
- backplane/cabling documentation
- spare and option part numbers
- supported CPU/NIC/HBA/storage option matrices
- SPP/SUM release documentation

## SPP/SUM preservation

The Gen8 Service Pack for ProLiant lineage is a high-priority preservation target because it represents a bundled, historically coherent firmware/driver baseline. Preserve exact ISO names, release dates, release notes, Smart Update Manager versions, vendor-published checksums, component inventories, and access requirements.

A gated HPE download remains a valid provenance record even when the binary cannot be mirrored.

## Operating-system support model

The platform inventory distinguishes:

- `hpe-proprietary` — HPE-supplied binary/utility;
- `vendor-upstream` — component-vendor package such as Intel/Broadcom/Emulex/QLogic;
- `linux-in-tree` — Linux kernel driver;
- `freebsd-in-tree` — FreeBSD driver;
- `openbsd-in-tree` — OpenBSD driver;
- `netbsd-in-tree` — NetBSD driver;
- `firmware-only` — common platform firmware independent of host OS;
- `unknown` — not yet characterized.

## Reference-host inventory

The exact openCUDA host inventory will be recorded separately from the generic platform catalogue. Evidence should include, as applicable:

```text
sudo dmidecode
sudo lshw -sanitize
lspci -nnvv
lspci -tv
lsblk -o NAME,MODEL,TRAN,HCTL,SIZE
ip -details link
ethtool -i <iface>
modinfo <driver>
uname -a
cat /etc/os-release
```

Also capture iLO inventory, Smart Array controller/firmware state, storage/backplane topology, PCIe riser population, exact FlexibleLOM/NIC option, and Cubix HIC slot/PCI identity.

Do not publish host serial numbers, UUIDs, MAC addresses, IP addresses, drive serial numbers, credentials, or other unnecessary unique identifiers.

## Validation state

This document begins as a preservation framework. A component is not considered validated for the reference server until its exact PCI/USB/platform identity and installed firmware are measured on the machine.

## Related work

- #32 — Cubix vendor continuity
- #33 — Cubix/Xpander asset preservation
- #34 — NVIDIA R470 kernel compatibility
- #36 — DL380p Gen8 platform preservation
