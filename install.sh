#!/usr/bin/env bash
# Install compress-pdf from GitHub releases (Linux).
# Usage: curl -fsSL https://raw.githubusercontent.com/flaviocpontes/compress_pdf/master/install.sh | bash
set -euo pipefail

REPO="flaviocpontes/compress_pdf"
VERSION="${VERSION:-latest}" # override: VERSION=v1.0.0 bash install.sh

[ "$(uname -s)" = "Linux" ] || { echo "Error: Linux only (got $(uname -s))" >&2; exit 1; }
case "$(uname -m)" in
  x86_64) target="linux-x86_64" ;;
  *) echo "Error: no prebuilt binary for $(uname -m). Build one with:" >&2
     echo "  git clone https://github.com/$REPO && cd compress_pdf && uv run pyinstaller --onefile --name compress-pdf main.py" >&2
     exit 1 ;;
esac

command -v curl >/dev/null || { echo "Error: curl is required" >&2; exit 1; }

if [ "$VERSION" = "latest" ]; then
  url="https://github.com/$REPO/releases/latest/download/compress-pdf-$target"
else
  url="https://github.com/$REPO/releases/download/$VERSION/compress-pdf-$target"
fi

# First writable directory on PATH wins; fall back to ~/.local/bin.
dest=""
oldifs="$IFS"
IFS=:
for dir in $PATH; do
  if [ -d "$dir" ] && [ -w "$dir" ]; then dest="$dir"; break; fi
done
IFS="$oldifs"
if [ -z "$dest" ]; then
  dest="$HOME/.local/bin"
  mkdir -p "$dest"
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "Downloading $url"
curl -fsSL "$url" -o "$tmp/compress-pdf-$target"
install_path="$dest/compress-pdf"
cp "$tmp/compress-pdf-$target" "$install_path"
chmod +x "$install_path"

# Smoke test: no args must exit 2 (usage error) — proves the binary executes
# (catches glibc-too-old failures).
set +e
"$install_path" >/dev/null 2>&1
rc=$?
set -e
[ "$rc" -eq 2 ] || echo "Warning: binary exited $rc on smoke test (missing/old glibc?)" >&2

case ":$PATH:" in
  *":$dest:"*) ;;
  *) echo "Note: $dest is not on your PATH. Add: export PATH=\"$dest:\$PATH\"" >&2 ;;
esac
echo "Installed $install_path"
