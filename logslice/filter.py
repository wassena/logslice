"""Log filtering and slicing by time range and pattern."""

from datetime import datetime
from typing import Iterator, Optional

from logslice.parser import extract_timestamp, matches_pattern


def filter_lines(
    lines: Iterator[str],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    pattern: Optional[str] = None,
    invert: bool = False,
) -> Iterator[str]:
    """Filter log lines by time range and/or pattern.

    Args:
        lines: Iterable of raw log lines.
        start: Include lines with timestamp >= start (inclusive).
        end: Include lines with timestamp <= end (inclusive).
        pattern: Regex or plain-text pattern to match against each line.
        invert: If True, return lines that do NOT match the pattern.

    Yields:
        Lines that satisfy all specified criteria.
    """
    for line in lines:
        stripped = line.rstrip("\n")

        if start is not None or end is not None:
            ts = extract_timestamp(stripped)
            if ts is not None:
                if start is not None and ts < start:
                    continue
                if end is not None and ts > end:
                    continue
            # Lines without a parseable timestamp are skipped when a
            # time range is requested.
            elif start is not None or end is not None:
                continue

        if pattern is not None:
            matched = matches_pattern(stripped, pattern)
            if invert and matched:
                continue
            if not invert and not matched:
                continue

        yield stripped


def slice_file(
    path: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    pattern: Optional[str] = None,
    invert: bool = False,
) -> Iterator[str]:
    """Open a log file and yield filtered lines.

    Args:
        path: Path to the log file.
        start: Lower bound for timestamp filtering.
        end: Upper bound for timestamp filtering.
        pattern: Pattern to match (or exclude when invert=True).
        invert: Invert pattern match logic.

    Yields:
        Filtered log lines (without trailing newline).
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        yield from filter_lines(fh, start=start, end=end, pattern=pattern, invert=invert)
