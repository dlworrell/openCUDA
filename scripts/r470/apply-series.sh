#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
CACHE=${R470_CACHE_DIR:-"$ROOT/.cache/r470"}
SERIES="$ROOT/patches/nvidia-r470/SERIES"
PATCH_UPSTREAM="$CACHE/upstream-patches"
WORK="$CACHE/work"

"$ROOT/scripts/r470/fetch-upstream.sh"

# shellcheck disable=SC1090
. "$ROOT/patches/nvidia-r470/UPSTREAM"

rm -rf "$WORK"
mkdir -p "$WORK"
(
    cd "$WORK"
    sh "$CACHE/$NVIDIA_RUNFILE" --extract-only >/dev/null
)

SOURCE="$WORK/NVIDIA-Linux-x86_64-$NVIDIA_DRIVER_VERSION"
KERNEL_SOURCE="$SOURCE/kernel"

if [ ! -d "$KERNEL_SOURCE" ]; then
    echo "error: extracted NVIDIA kernel-interface source not found at $KERNEL_SOURCE" >&2
    exit 4
fi

while IFS= read -r entry || [ -n "$entry" ]; do
    case "$entry" in
        ''|'#'*) continue ;;
        upstream/*)
            patch_file="$PATCH_UPSTREAM/${entry#upstream/}"
            ;;
        local/*)
            patch_file="$ROOT/patches/nvidia-r470/$entry"
            ;;
        staging/*)
            echo "error: staging patch listed in production SERIES: $entry" >&2
            exit 5
            ;;
        *)
            echo "error: invalid SERIES entry: $entry" >&2
            exit 6
            ;;
    esac

    if [ ! -f "$patch_file" ]; then
        echo "error: missing patch: $patch_file" >&2
        exit 7
    fi

    printf 'Applying %s\n' "$entry"
    patch --batch --forward -Np1 -d "$KERNEL_SOURCE" -i "$patch_file"
done < "$SERIES"

printf '%s\n' "Patched NVIDIA R470 source ready:" "  $SOURCE"
