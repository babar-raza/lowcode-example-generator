"""TIER-1 programmatic fixture generator for Imaging probe.

Generates a minimal valid PNG file (1x1 red pixel) using Python bytes only.
No binary files committed. No external dependencies.
"""

import struct
import zlib
from pathlib import Path


def create_minimal_png(path: str | Path) -> Path:
    """Create a minimal 1x1 red pixel PNG file.

    Uses Python bytes literals only — no Pillow, no external image library.
    The PNG is a valid 1x1 24-bit RGB image with a red pixel.
    """
    path = Path(path)

    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        length = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
        return length + chunk_type + data + crc

    # PNG signature
    sig = b"\x89PNG\r\n\x1a\n"

    # IHDR chunk: 1x1 RGB (8-bit)
    width = struct.pack(">I", 1)
    height = struct.pack(">I", 1)
    ihdr_data = width + height + bytes([8, 2, 0, 0, 0])  # 8 bit depth, RGB, no interlace
    ihdr = make_chunk(b"IHDR", ihdr_data)

    # IDAT chunk: raw pixel data (filter byte 0, then RGB values for red)
    raw_row = bytes([0, 255, 0, 0])  # filter=None, R=255, G=0, B=0
    compressed = zlib.compress(raw_row)
    idat = make_chunk(b"IDAT", compressed)

    # IEND chunk
    iend = make_chunk(b"IEND", b"")

    png_bytes = sig + ihdr + idat + iend
    path.write_bytes(png_bytes)
    return path


if __name__ == "__main__":
    out = create_minimal_png("input.png")
    print(f"Created: {out} ({out.stat().st_size} bytes)")
