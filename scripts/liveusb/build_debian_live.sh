#!/usr/bin/env bash
set -euo pipefail

readonly DEBIAN_DISTRIBUTION="bookworm"
readonly IMAGE_NAME="opencuda-dl380p-k80"
readonly DEFAULT_BUILD_DIR="${PWD}/build/liveusb-debian"

usage() {
    cat <<'EOF'
Usage: build_debian_live.sh [--check|--configure-only|--build] [--build-dir PATH]

Creates a Debian 12 (Bookworm) amd64 ISO-hybrid profile for the openCUDA
DL380p/CUBIX K80 scan. --build is the default and requires root plus live-build.
EOF
}

MODE=build
BUILD_DIR="$DEFAULT_BUILD_DIR"
while (( $# )); do
    case "$1" in
        --check) MODE=check ;;
        --configure-only) MODE=configure ;;
        --build) MODE=build ;;
        --build-dir)
            shift
            [[ $# -gt 0 ]] || { printf 'Missing value for --build-dir\n' >&2; exit 2; }
            BUILD_DIR="$1"
            ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'Unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

validate_sources() {
    local required
    for required in \
        "$SCRIPT_DIR/opencuda_usb_scan.sh" \
        "$SCRIPT_DIR/k80_staged_load.cu" \
        "$SCRIPT_DIR/opencuda-live-scan.service"; do
        [[ -s "$required" ]] || { printf 'Required source missing: %s\n' "$required" >&2; return 1; }
    done
    bash -n "$SCRIPT_DIR/opencuda_usb_scan.sh"
    grep -q 'DEFAULT_EXPECTED_K80_DEVICES=2' "$SCRIPT_DIR/opencuda_usb_scan.sh"
    grep -q 'VERIFIED-FORCED-AIRFLOW' "$SCRIPT_DIR/opencuda_usb_scan.sh"
    grep -q -- '--devices "$K80_DEVICE_LIST"' "$SCRIPT_DIR/opencuda_usb_scan.sh"
}

validate_sources
if [[ "$MODE" == check ]]; then
    printf 'Debian live-image source checks passed.\n'
    exit 0
fi

command -v lb >/dev/null 2>&1 || {
    printf 'live-build is required. On Debian: apt-get install live-build\n' >&2
    exit 1
}

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
lb clean --purge >/dev/null 2>&1 || true
lb config noauto \
    --mode debian \
    --distribution "$DEBIAN_DISTRIBUTION" \
    --architectures amd64 \
    --binary-images iso-hybrid \
    --debian-installer none \
    --archive-areas "main contrib non-free non-free-firmware" \
    --backports true \
    --firmware-chroot false \
    --apt-recommends false \
    --image-name "$IMAGE_NAME" \
    --iso-application "openCUDA DL380p K80 scanner" \
    --iso-publisher "openCUDA" \
    --bootappend-live "boot=live components hostname=opencuda-scan username=opencuda modprobe.blacklist=nouveau nouveau.modeset=0"

mkdir -p \
    config/package-lists \
    config/archives \
    config/includes.chroot/usr/local/sbin \
    config/includes.chroot/usr/local/libexec/opencuda \
    config/includes.chroot/etc/systemd/system/multi-user.target.wants \
    config/includes.chroot/etc/modprobe.d \
    config/hooks/live

cat >config/archives/bookworm-backports.pref.chroot <<'EOF'
Package: *nvidia-tesla-470*
Pin: release n=bookworm-backports
Pin-Priority: 990

Package: firmware-atheros firmware-brcm80211 firmware-iwlwifi firmware-libertas firmware-mediatek firmware-realtek
Pin: release n=bookworm-backports
Pin-Priority: 990
EOF
cp config/archives/bookworm-backports.pref.chroot \
    config/archives/bookworm-backports.pref.binary

cp "$SCRIPT_DIR/opencuda_usb_scan.sh" \
    config/includes.chroot/usr/local/sbin/opencuda_usb_scan.sh
cp "$SCRIPT_DIR/k80_staged_load.cu" \
    config/includes.chroot/usr/local/libexec/opencuda/k80_staged_load.cu
cp "$SCRIPT_DIR/opencuda-live-scan.service" \
    config/includes.chroot/etc/systemd/system/opencuda-live-scan.service
chmod 0755 config/includes.chroot/usr/local/sbin/opencuda_usb_scan.sh
ln -sfn /etc/systemd/system/opencuda-live-scan.service \
    config/includes.chroot/etc/systemd/system/multi-user.target.wants/opencuda-live-scan.service

cat >config/package-lists/opencuda.list.chroot <<'EOF'
live-boot
live-config
systemd-sysv
linux-image-amd64/bookworm-backports
linux-headers-amd64/bookworm-backports
nvidia-tesla-470-driver/bookworm-backports
nvidia-persistenced
nvidia-cuda-toolkit
nvidia-cuda-toolkit-gcc
network-manager
wpasupplicant
wireless-regdb
rfkill
firmware-atheros/bookworm-backports
firmware-brcm80211/bookworm-backports
firmware-iwlwifi/bookworm-backports
firmware-libertas/bookworm-backports
firmware-mediatek/bookworm-backports
firmware-realtek/bookworm-backports
curl
ca-certificates
pciutils
usbutils
dmidecode
lshw
numactl
ethtool
lm-sensors
ipmitool
smartmontools
nvme-cli
util-linux
gzip
tar
EOF

cat >config/includes.chroot/etc/modprobe.d/opencuda-nvidia.conf <<'EOF'
blacklist nouveau
options nouveau modeset=0
EOF

cat >config/hooks/live/0500-build-k80-helper.hook.chroot <<'EOF'
#!/bin/sh
set -eu
nvcc -O2 -std=c++14 -arch=sm_37 -cudart=static \
    --compiler-bindir=/usr/bin/g++-11 -Xcompiler=-pthread \
    /usr/local/libexec/opencuda/k80_staged_load.cu \
    -o /usr/local/libexec/opencuda/k80_staged_load
chmod 0755 /usr/local/libexec/opencuda/k80_staged_load
EOF
chmod 0755 config/hooks/live/0500-build-k80-helper.hook.chroot

cat >config/hooks/live/0600-record-image-stack.hook.chroot <<'EOF'
#!/bin/sh
set -eu
mkdir -p /usr/local/share/opencuda
{
    printf 'distribution=bookworm\n'
    dpkg-query -W -f='kernel=${Version}\n' linux-image-amd64
    dpkg-query -W -f='nvidia_driver=${Version}\n' nvidia-tesla-470-driver
    dpkg-query -W -f='cuda_toolkit=${Version}\n' nvidia-cuda-toolkit
} >/usr/local/share/opencuda/live-image-stack.txt
EOF
chmod 0755 config/hooks/live/0600-record-image-stack.hook.chroot

printf 'Configured Debian live-build profile at %s\n' "$BUILD_DIR"
if [[ "$MODE" == configure ]]; then
    exit 0
fi

(( EUID == 0 )) || {
    printf 'Run --build as root; --configure-only does not require root.\n' >&2
    exit 1
}
lb build 2>&1 | tee build.log

ISO_PATH="$BUILD_DIR/${IMAGE_NAME}-amd64.hybrid.iso"
[[ -s "$ISO_PATH" ]] || {
    printf 'Expected ISO not found: %s\n' "$ISO_PATH" >&2
    exit 1
}
sha256sum "$ISO_PATH" >"$ISO_PATH.sha256"
printf 'Built %s\n' "$ISO_PATH"
printf 'Checksum %s.sha256\n' "$ISO_PATH"
