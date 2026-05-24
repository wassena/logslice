"""Pattern highlighting support for logslice output."""

import re
from typing import List, Optional

# ANSI color codes
ANSI_RESET = "\033[0m"
ANSI_BOLD_YELLOW = "\033[1;33m"
ANSI_BOLD_RED = "\033[1;31m"
ANSI_BOLD_CYAN = "\033[1;36m"

HIGHLIGHT_COLORS = [
    ANSI_BOLD_YELLOW,
    ANSI_BOLD_RED,
    ANSI_BOLD_CYAN,
]


def highlight_pattern(line: str, pattern: str, color: Optional[str] = None) -> str:
    """Highlight all occurrences of pattern in line with ANSI color codes.

    Args:
        line: The text line to highlight.
        pattern: Regex pattern to search for.
        color: ANSI escape code to use; defaults to bold yellow.

    Returns:
        Line with matching substrings wrapped in ANSI codes.
    """
    if not pattern:
        return line

    if color is None:
        color = ANSI_BOLD_YELLOW

    try:
        highlighted = re.sub(
            pattern,
            lambda m: f"{color}{m.group(0)}{ANSI_RESET}",
            line,
            flags=re.IGNORECASE,
        )
    except re.error:
        # Fall back to literal string replacement if pattern is invalid
        escaped = re.escape(pattern)
        highlighted = re.sub(
            escaped,
            lambda m: f"{color}{m.group(0)}{ANSI_RESET}",
            line,
            flags=re.IGNORECASE,
        )
    return highlighted


def highlight_multiple(line: str, patterns: List[str]) -> str:
    """Highlight multiple patterns in a line, each with a distinct color.

    Args:
        line: The text line to highlight.
        patterns: List of regex patterns to highlight.

    Returns:
        Line with all matching patterns highlighted in different colors.
    """
    for i, pattern in enumerate(patterns):
        color = HIGHLIGHT_COLORS[i % len(HIGHLIGHT_COLORS)]
        line = highlight_pattern(line, pattern, color)
    return line


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text.

    Args:
        text: Text potentially containing ANSI codes.

    Returns:
        Plain text with all ANSI codes removed.
    """
    ansi_escape = re.compile(r"\033\[[0-9;]*m")
    return ansi_escape.sub("", text)
