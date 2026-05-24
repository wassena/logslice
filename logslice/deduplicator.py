"""Deduplication support for log lines."""

import hashlib
from collections import OrderedDict
from typing import Iterable, Iterator, Optional


def _line_key(line: str, ignore_timestamps: bool = False) -> str:
    """Compute a deduplication key for a line."""
    if ignore_timestamps:
        # Strip leading timestamp-like prefix (up to first ']' or ':' block)
        import re
        cleaned = re.sub(
            r'^[\[\(]?[\d\-T:.Z/\s]+[\]\)]?[\s:\|]+', '', line.strip()
        )
        return hashlib.md5(cleaned.encode()).hexdigest()
    return hashlib.md5(line.strip().encode()).hexdigest()


def deduplicate_lines(
    lines: Iterable[str],
    ignore_timestamps: bool = False,
    max_cache: int = 10_000,
) -> Iterator[str]:
    """Yield unique lines, dropping exact (or timestamp-normalized) duplicates.

    Args:
        lines: Iterable of log line strings.
        ignore_timestamps: If True, lines that differ only in timestamp are
            considered duplicates.
        max_cache: Maximum number of keys to keep in the seen-set. Oldest
            entries are evicted when the limit is reached (LRU-style via
            OrderedDict).

    Yields:
        Lines that have not been seen before.
    """
    seen: OrderedDict[str, None] = OrderedDict()

    for line in lines:
        key = _line_key(line, ignore_timestamps=ignore_timestamps)
        if key in seen:
            seen.move_to_end(key)
            continue
        seen[key] = None
        if len(seen) > max_cache:
            seen.popitem(last=False)
        yield line


def count_duplicates(
    lines: Iterable[str],
    ignore_timestamps: bool = False,
) -> tuple[int, int]:
    """Return (total, unique) counts for a collection of lines."""
    seen: set[str] = set()
    total = 0
    for line in lines:
        total += 1
        seen.add(_line_key(line, ignore_timestamps=ignore_timestamps))
    return total, len(seen)
