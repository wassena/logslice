"""Log line parser for extracting timestamps and patterns from log entries."""

import re
from datetime import datetime
from typing import Optional

# Common log timestamp formats
TIMESTAMP_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%d/%b/%Y:%H:%M:%S %z",  # Apache/Nginx combined log format
    "%b %d %H:%M:%S",        # syslog format
]

TIMESTAMP_PATTERNS = [
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)",
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)",
    r"(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})",
    r"(\w{3} +\d{1,2} \d{2}:\d{2}:\d{2})",
]


def extract_timestamp(line: str) -> Optional[datetime]:
    """Extract and parse the first timestamp found in a log line."""
    for pattern in TIMESTAMP_PATTERNS:
        match = re.search(pattern, line)
        if match:
            raw = match.group(1)
            for fmt in TIMESTAMP_FORMATS:
                try:
                    return datetime.strptime(raw, fmt)
                except ValueError:
                    continue
    return None


def matches_pattern(line: str, pattern: str, case_sensitive: bool = False) -> bool:
    """Check whether a log line matches a given regex or substring pattern."""
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        return bool(re.search(pattern, line, flags))
    except re.error:
        # Fall back to plain substring match if pattern is not valid regex
        if case_sensitive:
            return pattern in line
        return pattern.lower() in line.lower()


def parse_line(line: str) -> dict:
    """Parse a log line into a structured dict with timestamp and raw text."""
    line = line.rstrip("\n")
    return {
        "raw": line,
        "timestamp": extract_timestamp(line),
    }
