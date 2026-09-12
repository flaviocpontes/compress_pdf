import os
import random
import tempfile

import fitz

from main import compress_to_target


def make_scan_pdf(path, pages=3, big=True):
    rng = random.Random(42)
    doc = fitz.open()
    dim = 2000 if big else 50
    cell = 40 if big else 10
    for _ in range(pages):
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, dim, dim))
        pix.clear_with(200)
        for y in range(0, dim, cell):  # noise-like pattern: hard to compress, like a real scan
            for x in range(0, dim, cell):
                pix.set_rect(fitz.IRect(x, y, x + cell, y + cell), (rng.randrange(256), rng.randrange(256), rng.randrange(256)))
        page = doc.new_page(width=612, height=792)
        page.insert_image(page.rect, pixmap=pix)
    doc.save(path)
    doc.close()


def check(path, pages, max_mib=None):
    assert os.path.exists(path), f"{path} was not written"
    doc = fitz.open(path)
    assert len(doc) == pages, f"expected {pages} pages, got {len(doc)}"
    assert doc[0].rect.width == 612 and doc[0].rect.height == 792, (
        f"page size not preserved: {doc[0].rect}"
    )
    doc.close()
    size_mib = os.path.getsize(path) / (1024 * 1024)
    if max_mib is not None:
        assert size_mib <= max_mib, f"{size_mib:.2f} MiB exceeds target {max_mib} MiB"
    return size_mib


def test_compresses_big_scan(tmp):
    src = os.path.join(tmp, "big.pdf")
    out = os.path.join(tmp, "big_out.pdf")
    make_scan_pdf(src, pages=3)
    size = compress_to_target(src, out, 0.2)
    assert size <= 0.2 * 1024 * 1024, f"did not reach target: {size}"
    check(out, pages=3, max_mib=0.2)


def test_already_small_passthrough(tmp):
    src = os.path.join(tmp, "small.pdf")
    out = os.path.join(tmp, "small_out.pdf")
    make_scan_pdf(src, pages=1, big=False)
    compress_to_target(src, out, 1)
    check(out, pages=1, max_mib=1)


def test_unreachable_target_still_writes(tmp):
    src = os.path.join(tmp, "big2.pdf")
    out = os.path.join(tmp, "big2_out.pdf")
    make_scan_pdf(src, pages=3)
    size = compress_to_target(src, out, 0.01)
    assert size > 0.01 * 1024 * 1024, "should not have reached an impossible target"
    check(out, pages=3)  # best-effort file must still be valid


def main():
    tests = [
        test_compresses_big_scan,
        test_already_small_passthrough,
        test_unreachable_target_still_writes,
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for test in tests:
            test(tmp)
            print(f"PASS {test.__name__}")
    print("All tests passed.")


if __name__ == "__main__":
    main()
