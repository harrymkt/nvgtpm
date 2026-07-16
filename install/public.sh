#!/usr/bin/env bash
set -e

# NVGTPM installer
# This is the public version.

NVGT_BIN="$(command -v nvgt || true)"

if [ -z "$NVGT_BIN" ]; then
  echo "Error: NVGT not found in PATH"
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

URL="https://github.com/harrymkt/nvgtpm/releases/latest/download/${FILE}"
curl -fL "$URL" -o "$OUT"

chmod +x "$OUT" 2>/dev/null || true
sudo mv "$OUT" "$NVGT_DIR/"
echo "NVGTPM installed to $NVGT_DIR"
