#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
META="$ROOT/patches/nvidia-r470/UPSTREAM"
CACHE=${R470_CACHE_DIR:-"$ROOT/.cache/r470"}
PATCH_DST="$CACHE/upstream-patches"

# shellcheck disable=SC1090
. "$META"

mkdir -p "$CACHE"

RUNFILE="$CACHE/$NVIDIA_RUNFILE"
if [ ! -f "$RUNFILE" ]; then
    if command -v curl >/dev/null 2>&1; then
        curl --fail --location --proto '=https' --tlsv1.2 \
            --output "$RUNFILE.tmp" "$NVIDIA_RUNFILE_URL"
    elif command -v wget >/dev/null 2>&1; then
        wget --https-only --output-document="$RUNFILE.tmp" "$NVIDIA_RUNFILE_URL"
    else
        echo "error: curl or wget is required" >&2
        exit 2
    fi
    mv "$RUNFILE.tmp" "$RUNFILE"
fi

(
    cd "$CACHE"
    sha512sum --check "$ROOT/patches/nvidia-r470/SHA512SUMS"
)

rm -rf "$CACHE/patch-upstream" "$PATCH_DST"
git clone --quiet --no-checkout "$PATCH_UPSTREAM_REPOSITORY" "$CACHE/patch-upstream"
git -C "$CACHE/patch-upstream" checkout --quiet --detach "$PATCH_UPSTREAM_COMMIT"

actual_commit=$(git -C "$CACHE/patch-upstream" rev-parse HEAD)
if [ "$actual_commit" != "$PATCH_UPSTREAM_COMMIT" ]; then
    echo "error: upstream patch checkout mismatch: $actual_commit" >&2
    exit 3
fi

mkdir -p "$PATCH_DST"
cp "$CACHE/patch-upstream/$PATCH_UPSTREAM_PATH"/*.patch "$PATCH_DST"/

printf '%s\n' "R470 inputs ready:" \
    "  NVIDIA runfile: $RUNFILE" \
    "  upstream patches: $PATCH_DST" \
    "  pinned commit: $PATCH_UPSTREAM_COMMIT"
