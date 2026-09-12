import sys
import os
import fitz


def collect_image_xrefs(doc):
    xrefs = set()
    for page in doc:
        for img in page.get_images(full=True):
            xrefs.add(img[0])
        for xref in page.xrefs():
            try:
                if doc.xref_get_key(xref, "Subtype")[1] == "/XObject":
                    if doc.xref_get_key(xref, "Subtype")[1] == "/Image":
                        xrefs.add(xref)
            except Exception:
                pass
    return xrefs


def recompress_images(doc, quality):
    replaced = 0
    for page in doc:
        for img_index in page.get_images(full=True):
            xref = img_index[0]
            try:
                img = doc.extract_image(xref)
                if img["ext"] == "jpeg":
                    continue
                pix = fitz.Pixmap(doc, xref)
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                jpeg_bytes = pix.tobytes("jpeg", quality=quality)
                new_pix = fitz.Pixmap(jpeg_bytes)
                rect = page.get_image_rects(xref)[0]
                page.replace_image(xref, pixmap=new_pix)
                replaced += 1
            except Exception:
                pass
    return replaced


def save_with_options(doc, path, garbage=3, deflate=True):
    doc.save(path, garbage=garbage, deflate=deflate)


def compress_to_target(input_path, output_path, target_mib):
    target_bytes = target_mib * 1024 * 1024
    doc = fitz.open(input_path)

    save_with_options(doc, output_path)
    if os.path.getsize(output_path) <= target_bytes:
        print(f"Already within target: {os.path.getsize(output_path) / (1024*1024):.2f} MiB")
        doc.close()
        return

    qualities = [95, 85, 75, 65, 55, 45, 35, 25, 15]
    best_quality = qualities[-1]
    best_path = output_path

    for quality in qualities:
        doc_copy = fitz.open(doc.name)
        recompress_images(doc_copy, quality)
        temp_path = output_path + f".tmp_q{quality}"
        save_with_options(doc_copy, temp_path)
        size = os.path.getsize(temp_path)
        print(f"  Quality {quality}: {size / (1024*1024):.2f} MiB")
        doc_copy.close()

        if size <= target_bytes:
            best_quality = quality
            best_path = temp_path
            break
        elif size < os.path.getsize(best_path) if os.path.exists(best_path) else True:
            best_quality = quality
            best_path = temp_path

    if best_path != output_path:
        os.replace(best_path, output_path)

    for q in qualities:
        tmp = output_path + f".tmp_q{q}"
        if os.path.exists(tmp):
            os.remove(tmp)

    final_size = os.path.getsize(output_path)
    print(f"Final: {final_size / (1024*1024):.2f} MiB (quality={best_quality})")
    doc.close()


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <input.pdf> <output.pdf> <size_in_mib>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    target_mib = float(sys.argv[3])

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found")
        sys.exit(1)

    compress_to_target(input_path, output_path, target_mib)


if __name__ == "__main__":
    main()
