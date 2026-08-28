#!/usr/bin/env bash
set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly BUILDER="$REPO_ROOT/scripts/liveusb/build_debian_live.sh"

bash -n "$BUILDER"
output="$(bash "$BUILDER" --check)"
grep -q 'source checks passed' <<<"$output"
grep -q 'bookworm' "$BUILDER"
grep -q 'linux-image-amd64/bookworm-backports' "$BUILDER"
grep -q 'Pin-Priority: 990' "$BUILDER"
grep -q 'nvidia-tesla-470-driver/bookworm-backports' "$BUILDER"
grep -q 'nvidia-cuda-toolkit' "$BUILDER"
grep -q 'nvidia-cuda-toolkit-gcc' "$BUILDER"
grep -q 'firmware-realtek' "$BUILDER"
grep -q 'firmware-atheros' "$BUILDER"
grep -q 'sm_37' "$BUILDER"
grep -q 'opencuda-live-scan.service' "$BUILDER"

if grep -Eqi '(app.password|wifi.password|gmail[^[:space:]]*@)' "$BUILDER"; then
    printf 'Builder appears to contain a credential or email address\n' >&2
    exit 1
fi

printf 'Debian live-image builder tests passed.\n'
