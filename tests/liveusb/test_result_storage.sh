#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly SCANNER="$REPO_ROOT/scripts/liveusb/opencuda_usb_scan.sh"

fixture="$(mktemp -d)"
trap 'rm -rf "$fixture"' EXIT
mkdir -p "$fixture/bin" "$fixture/mounted" "$fixture/auto-mount"

make_stub() {
    local name="$1"
    shift
    printf '%s\n' '#!/usr/bin/env bash' "$@" >"$fixture/bin/$name"
    chmod +x "$fixture/bin/$name"
}

make_stub blkid 'printf "%s\n" "${TEST_BLKID_OUTPUT:-}"'
make_stub lsblk \
    'case "$*" in' \
    '  *" RM "*) printf "%s\n" "${TEST_RM:-}" ;;' \
    '  *" TRAN "*) printf "%s\n" "${TEST_TRAN:-}" ;;' \
    '  *" TYPE "*) printf "%s\n" "${TEST_TYPE:-}" ;;' \
    'esac'
make_stub findmnt \
    'if [[ -n "${TEST_MOUNTED_TARGET:-}" ]]; then printf "%s\n" "$TEST_MOUNTED_TARGET"; fi'
make_stub mount \
    'printf "%s\n" "$*" >>"${TEST_MOUNT_LOG:?}"'
make_stub umount 'exit 0'

export PATH="$fixture/bin:$PATH"
export TEST_MOUNT_LOG="$fixture/mount.log"
export TEST_BLKID_OUTPUT=/dev/test-data1
export TEST_RM=1
export TEST_TRAN=usb
export TEST_TYPE=part

# Sourcing exposes the storage functions without launching the interactive scan.
# shellcheck source=../../scripts/liveusb/opencuda_usb_scan.sh
source "$SCANNER"

test "$(discover_result_device)" = /dev/test-data1

export TEST_MOUNTED_TARGET="$fixture/mounted"
RESULT_ROOT=""
mount_result_device /dev/test-data1
test "$RESULT_ROOT" = "$fixture/mounted/opencuda-results"
test ! -e "$fixture/mount.log"

export TEST_MOUNTED_TARGET=""
export OPENCUDA_DATA_MOUNTPOINT="$fixture/auto-mount"
RESULT_ROOT=""
mount_result_device /dev/test-data1
test "$RESULT_ROOT" = "$fixture/auto-mount/opencuda-results"
grep -q -- '-o rw,nosuid,nodev,noexec /dev/test-data1' "$fixture/mount.log"

export TEST_RM=0
export TEST_TRAN=sata
if discover_result_device >/dev/null 2>&1; then
    printf 'Internal storage was incorrectly accepted as OPENCUDA_DATA.\n' >&2
    exit 1
fi

export TEST_RM=1
export TEST_TRAN=usb
export TEST_BLKID_OUTPUT=$'/dev/test-data1\n/dev/test-data2'
if discover_result_device >/dev/null 2>&1; then
    printf 'Ambiguous OPENCUDA_DATA labels were incorrectly accepted.\n' >&2
    exit 1
fi

printf 'removable result-storage tests passed\n'
