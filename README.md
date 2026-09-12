# compress-pdf

Compress a PDF to a target file size by re-encoding its images.

## Usage

```bash
uv run main.py <input.pdf> <output.pdf> <size_in_mib>
```

Example:

```bash
uv run main.py big.pdf small.pdf 5
```

Compresses `big.pdf` to at most 5 MiB by re-encoding images at decreasing
JPEG quality (95→15) until the target is met. If the file is already within
the target, it is simply optimized and saved.
