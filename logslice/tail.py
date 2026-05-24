"""Tail support: read last N lines or follow a growing log file."""

import os
import time
from typing import Generator, List

from logslice.reader import open_log_file

_BLOCK_SIZE = 8192


def tail_lines(filepath: str, n: int = 10) -> List[str]:
    """Return the last n lines of a plain-text log file efficiently."""
    if n <= 0:
        return []

    try:
        with open(filepath, "rb") as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            if file_size == 0:
                return []

            buffer = b""
            remaining = file_size
            lines_found = 0

            while remaining > 0 and lines_found <= n:
                block = min(_BLOCK_SIZE, remaining)
                remaining -= block
                f.seek(remaining)
                chunk = f.read(block)
                buffer = chunk + buffer
                lines_found = buffer.count(b"\n")

        decoded = buffer.decode("utf-8", errors="replace")
        all_lines = decoded.splitlines(keepends=True)
        return all_lines[-n:]
    except OSError as exc:
        raise FileNotFoundError(f"Cannot tail file: {filepath}") from exc


def follow(
    filepath: str,
    poll_interval: float = 0.5,
    max_wait: float = 0.0,
) -> Generator[str, None, None]:
    """Follow a log file, yielding new lines as they are appended.

    Args:
        filepath: Path to the log file.
        poll_interval: Seconds between polls.
        max_wait: Stop after this many seconds of no new data (0 = run forever).
    """
    with open_log_file(filepath) as f:
        f.seek(0, os.SEEK_END)
        idle = 0.0
        while True:
            line = f.readline()
            if line:
                idle = 0.0
                yield line
            else:
                time.sleep(poll_interval)
                idle += poll_interval
                if max_wait > 0 and idle >= max_wait:
                    return
