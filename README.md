# compress-pdf

Compress a PDF to a target file size by re-encoding its pages as JPEG
(downsampling resolution and quality as needed, color preferred over
grayscale).

## Install (Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/flaviocpontes/compress_pdf/master/install.sh | bash
```

Downloads the latest release binary and copies it to the first writable
directory on your `PATH` (creating `~/.local/bin` as a fallback). Install a
specific version with `VERSION=v1.0.0`. Requires a tagged release to exist.

## Usage

```bash
compress-pdf <input.pdf> <output.pdf> <size_in_mib>
```

Example:

```bash
compress-pdf big.pdf small.pdf 1
```

(Without building, you can also run it via `uv run main.py big.pdf small.pdf 1`.)

Tries a ladder of settings — 300/200/150/120 dpi at JPEG quality 60/40/25,
color first, grayscale as fallback — and stops at the first combination that
fits within the target. Exits with code 1 if even the smallest setting cannot
reach the target (the best-effort file is still written, with a warning). If
the input is already within the target after optimization, it is copied
through untouched.

Note: pages are rasterized (text layers are not preserved). Intended for
scanned documents.

## Build & install

Build a self-contained executable with PyInstaller (a dev dependency —
Python interpreter and PyMuPDF are bundled into a single ~38 MB file):

```bash
uv run pyinstaller --onefile --name compress-pdf main.py
```

This produces `dist/compress-pdf`. Install it somewhere on your `PATH`
(`~/.local/bin` is usual on Linux) and invoke it from anywhere:

```bash
cp dist/compress-pdf ~/.local/bin/
compress-pdf big.pdf small.pdf 1
```

Notes:

- The binary is platform-specific: it only runs on the OS/architecture
  that built it (here, Linux x86-64). No cross-compilation; build on the
  target platform.
- `--onefile` self-extracts to a temp dir on each run, adding ~0.5 s
  startup. Prefer `--onedir` if startup time matters more than having a
  single file.
- Build artifacts (`build/`, `dist/`, `*.spec`) are gitignored.
- Rebuild and re-copy after changing `main.py` — the installed binary is
  a snapshot, not a symlink.

## Testing

```bash
uv run tests.py
```

Generates synthetic scan-like PDFs and verifies three cases: a large scan is
compressed under the target with pages and page size intact, an
already-small file passes through, and an impossible target still produces a
valid best-effort file. Exits non-zero on any failure.
