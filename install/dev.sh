#!/usr/bin/env bash
set -e

NVGT_BIN="$(command -v nvgt || true)"

if [ -z "$NVGT_BIN" ]; then
  echo "Error: nvgt not found in PATH"
  exit 1
fi

NVGT_DIR="$(dirname "$NVGT_BIN")"

OS="$(uname -s)"

case "$OS" in
  Linux)
    FILE="nvgtpm-linux"
    OUT="nvgtpm"
    ;;
  Darwin)
    FILE="nvgtpm-macos"
    OUT="nvgtpm"
    ;;
  *)
    echo "Unsupported OS: $OS"
    exit 1
    ;;
esac

URL="https://github.com/harrymkt/nvgtpm/releases/download/dev/${FILE}"

curl -fL "$URL" -o "$OUT"

chmod +x "$OUT" 2>/dev/null || true

sudo mv "$OUT" "$NVGT_DIR/"

echo "NVGTPM development version installed to $NVGT_DIR"
