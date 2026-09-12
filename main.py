import os
import sys

import fitz

# First (dpi, quality, colorspace) whose output fits the target wins.
# Color is preferred; grayscale is the fallback. Quality alone is not enough:
# a 300 dpi scan never re-encodes below ~2 MiB, so downsampling is required.
STEPS = [
    (dpi, quality, fitz.csRGB)
    for dpi in (300, 200, 150, 120)
    for quality in (60, 40, 25)
] + [
    (dpi, quality, fitz.csGRAY)
    for dpi in (200, 150, 120)
    for quality in (60, 40, 25)
]


def build_pdf_bytes(doc, dpi, quality, colorspace):
    # ponytail: page-render rasterizes everything (text/vector too); fine for
    # scanned docs, replace with per-image xref handling if text layers matter
    out = fitz.open()
    scale = dpi / 72
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=colorspace)
        jpeg = pix.tobytes("jpeg", jpg_quality=quality)
        new_page = out.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=jpeg)
    return out.tobytes(garbage=3, deflate=True)


def compress_to_target(input_path, output_path, target_mib):
    target_bytes = target_mib * 1024 * 1024
    doc = fitz.open(input_path)

    optimized = doc.tobytes(garbage=3, deflate=True)
    if len(optimized) <= target_bytes:
        with open(output_path, "wb") as f:
            f.write(optimized)
        print(f"Already within target: {len(optimized) / (1024 * 1024):.2f} MiB")
        return len(optimized)

    pdf_bytes = b""
    for dpi, quality, colorspace in STEPS:
        pdf_bytes = build_pdf_bytes(doc, dpi, quality, colorspace)
        mode = "gray" if colorspace is fitz.csGRAY else "color"
        print(f"  {dpi}dpi {mode} q{quality}: {len(pdf_bytes) / (1024 * 1024):.2f} MiB")
        if len(pdf_bytes) <= target_bytes:
            break

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)
    final_mib = len(pdf_bytes) / (1024 * 1024)
    if len(pdf_bytes) <= target_bytes:
        print(f"Final: {final_mib:.2f} MiB")
    else:
        print(f"Warning: target unreachable, best effort {final_mib:.2f} MiB")
    return len(pdf_bytes)


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <input.pdf> <output.pdf> <size_in_mib>")
        sys.exit(2)

    input_path, output_path, target_mib = sys.argv[1], sys.argv[2], float(sys.argv[3])

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found")
        sys.exit(2)

    final_size = compress_to_target(input_path, output_path, target_mib)
    if final_size > target_mib * 1024 * 1024:
        sys.exit(1)


if __name__ == "__main__":
    main()
