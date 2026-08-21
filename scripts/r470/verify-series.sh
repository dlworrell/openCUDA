#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
SERIES="$ROOT/patches/nvidia-r470/SERIES"
META="$ROOT/patches/nvidia-r470/UPSTREAM"

# shellcheck disable=SC1090
. "$META"

fail=0
seen=''

while IFS= read -r entry || [ -n "$entry" ]; do
    case "$entry" in
        ''|'#'*) continue ;;
        staging/*)
            echo "error: staging patch present in production SERIES: $entry" >&2
            fail=1
            ;;
        upstream/*|local/*) ;;
        *)
            echo "error: invalid SERIES entry: $entry" >&2
            fail=1
            ;;
    esac

    case "\n$seen\n" in
        *"\n$entry\n"*)
            echo "error: duplicate SERIES entry: $entry" >&2
            fail=1
            ;;
        *) seen="$seen\n$entry" ;;
    esac

done < "$SERIES"

case "$PATCH_UPSTREAM_COMMIT" in
    [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*) ;;
    *) echo "error: PATCH_UPSTREAM_COMMIT is not a pinned Git commit" >&2; fail=1 ;;
esac

if ! grep -q "  $NVIDIA_RUNFILE\$" "$ROOT/patches/nvidia-r470/SHA256SUMS"; then
    echo "error: NVIDIA runfile missing from SHA256SUMS" >&2
    fail=1
fi

for dir in local staging; do
    if [ ! -f "$ROOT/patches/nvidia-r470/$dir/README.md" ]; then
        echo "error: missing policy file patches/nvidia-r470/$dir/README.md" >&2
        fail=1
    fi
done

[ "$fail" -eq 0 ] || exit 1
printf '%s\n' "R470 series metadata checks passed." \
    "driver=$NVIDIA_DRIVER_VERSION" \
    "patch-upstream=$PATCH_UPSTREAM_COMMIT"
