"""Log file reader with support for plain text and gzipped files."""

import gzip
import os
from typing import Generator, Tuple


def detect_encoding(filepath: str) -> str:
    """Attempt to detect file encoding, defaulting to utf-8."""
    encodings = ["utf-8", "latin-1", "ascii"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                f.read(1024)
            return enc
        except (UnicodeDecodeError, ValueError):
            continue
    return "utf-8"


def is_gzipped(filepath: str) -> bool:
    """Check if a file is gzip-compressed by reading its magic bytes."""
    try:
        with open(filepath, "rb") as f:
            return f.read(2) == b"\x1f\x8b"
    except OSError:
        return False


def open_log_file(filepath: str):
    """Open a log file for reading, handling gzip transparently."""
    if is_gzipped(filepath):
        return gzip.open(filepath, "rt", encoding="utf-8", errors="replace")
    encoding = detect_encoding(filepath)
    return open(filepath, "r", encoding=encoding, errors="replace")


def iter_lines(
    filepath: str, start_byte: int = 0
) -> Generator[Tuple[int, int, str], None, None]:
    """Iterate over lines in a log file.

    Yields tuples of (line_number, byte_offset, line_content).
    start_byte allows resuming from a specific offset (plain text only).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Log file not found: {filepath}")

    line_number = 0
    with open_log_file(filepath) as f:
        if start_byte > 0 and not is_gzipped(filepath):
            f.seek(start_byte)
        for line in f:
            line_number += 1
            try:
                byte_offset = f.tell()
            except OSError:
                byte_offset = -1
            yield line_number, byte_offset, line


def count_lines(filepath: str) -> int:
    """Count total number of lines in a log file."""
    count = 0
    with open_log_file(filepath) as f:
        for _ in f:
            count += 1
    return count
