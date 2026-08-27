#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fixture="$(mktemp -d)"
trap 'rm -rf "$fixture"' EXIT
mkdir -p "$fixture/bin" "$fixture/liveusb" "$fixture/results"
cp "$repo_root/scripts/liveusb/opencuda_usb_scan.sh" "$fixture/liveusb/"
cp "$repo_root/scripts/liveusb/k80_staged_load.cu" "$fixture/liveusb/"

make_stub() {
    local name="$1"
    shift
    printf '%s\n' '#!/usr/bin/env bash' "$@" >"$fixture/bin/$name"
    chmod +x "$fixture/bin/$name"
}

make_stub nmcli \
    'if [[ "$*" == *"device wifi list"* ]]; then echo "  test-net 100 WPA2"; fi' \
    'exit 0'

make_stub nvidia-smi \
    'args="$*"' \
    'if [[ "$args" == *"--query-gpu=index,name"* ]]; then' \
    '  printf "%s\n" "0, Tesla K80" "1, Tesla K80" "2, Quadro 6000"' \
    'elif [[ "$args" == *"--query-gpu=index --format"* ]]; then' \
    '  printf "%s\n" 0 1 2' \
    'elif [[ "$args" == *"--query-gpu=timestamp,index"* ]]; then' \
    '  printf "%s\n" "2026/08/27 00:00:00, 0, 0000:01:00.0, 40, 120, 25, P0, 700, 0" "2026/08/27 00:00:00, 1, 0000:02:00.0, 41, 121, 25, P0, 700, 0" "2026/08/27 00:00:00, 2, 0000:03:00.0, 35, 20, 0, P8, 50, N/A"' \
    'elif [[ "$args" == *"--query-gpu="* ]]; then' \
    '  printf "%s\n" "0, Tesla K80" "1, Tesla K80" "2, Quadro 6000"' \
    'else' \
    '  echo "mock nvidia-smi"' \
    'fi'

make_stub curl 'exit 0'
make_stub dmidecode 'echo "Serial Number: SECRET"'
make_stub lspci 'echo "mock PCIe"'
make_stub lsusb 'echo "iSerial 3 SECRET"'
make_stub ipmitool 'echo "mock IPMI"'
make_stub sensors 'echo "mock sensors"'
make_stub numactl 'echo "mock NUMA"'
make_stub lsmod 'echo "mock modules"'

printf '%s\n' '#!/usr/bin/env bash' \
    'printf "%s\n" "$*" >>"${OPENCUDA_TEST_LOAD_LOG:?}"' \
    'exit 0' >"$fixture/liveusb/k80_staged_load"
chmod +x "$fixture/liveusb/k80_staged_load"

export OPENCUDA_TEST_LOAD_LOG="$fixture/load.log"
export OPENCUDA_RESULT_ROOT="$fixture/results"
export OPENCUDA_IDLE_SECONDS=1
export OPENCUDA_PARTIAL_SECONDS=1
export OPENCUDA_FULL_SECONDS=1

PATH="$fixture/bin:$PATH" bash "$fixture/liveusb/opencuda_usb_scan.sh" <<'EOF'
test-net
VERIFIED-FORCED-AIRFLOW
scanner@example.com
test app password
EOF

run_dir="$(find "$fixture/results" -mindepth 1 -maxdepth 1 -type d | head -n1)"
test -n "$run_dir"
test -f "$run_dir/opencuda-scan-results.tar.gz"
grep -q 'Final status: `PASS`' "$run_dir/report.md"
grep -q -- '--devices 0,1' "$fixture/load.log"
if grep -q -- '--devices 0,1,2' "$fixture/load.log"; then
    echo 'Quadro device was incorrectly selected for load' >&2
    exit 1
fi
if grep -q 'SECRET' "$run_dir/report.md"; then
    echo 'sanitization fixture leaked a unique identifier' >&2
    exit 1
fi

printf '%s\n' 'live-USB scan fixture passed'
