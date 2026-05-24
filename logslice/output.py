"""Output formatting and writing utilities for logslice."""

import sys
from typing import Iterable, Optional, TextIO


DEFAULT_SEPARATOR = "\n"


def format_line(line: str, line_number: Optional[int] = None, colorize: bool = False) -> str:
    """Format a single log line, optionally with line number prefix."""
    line = line.rstrip("\n")
    if line_number is not None:
        prefix = f"{line_number:>6}: "
        if colorize:
            prefix = f"\033[90m{prefix}\033[0m"
        return f"{prefix}{line}"
    return line


def write_lines(
    lines: Iterable[str],
    output: TextIO = sys.stdout,
    line_numbers: bool = False,
    colorize: bool = False,
    count_only: bool = False,
) -> int:
    """Write filtered lines to the given output stream.

    Returns the total number of lines written.
    """
    count = 0
    for i, line in enumerate(lines, start=1):
        count += 1
        if not count_only:
            formatted = format_line(line, line_number=i if line_numbers else None, colorize=colorize)
            output.write(formatted + "\n")

    if count_only:
        output.write(f"{count}\n")

    return count


def write_summary(count: int, output: TextIO = sys.stderr) -> None:
    """Write a summary of matched lines to stderr."""
    label = "line" if count == 1 else "lines"
    output.write(f"[logslice] {count} matching {label}\n")
