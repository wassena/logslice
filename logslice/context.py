"""Context lines support: capture N lines before/after each match."""

from collections import deque
from typing import Iterator, List, Tuple, Optional


def iter_with_context(
    lines: List[str],
    before: int = 0,
    after: int = 0,
    match_fn=None,
) -> Iterator[Tuple[int, str, bool]]:
    """
    Yield (line_number, line, is_match) tuples, including context lines
    around each match.

    Args:
        lines: List of log lines to process.
        before: Number of lines to include before each match.
        after: Number of lines to include after each match.
        match_fn: Callable(line) -> bool. If None, all lines are matches.

    Yields:
        (1-based line number, line content, is_direct_match)
    """
    if match_fn is None:
        match_fn = lambda _: True

    before_buf: deque = deque(maxlen=before if before > 0 else 1)
    after_countdown: int = 0
    emitted: set = set()

    total = len(lines)

    for idx, line in enumerate(lines):
        lineno = idx + 1
        is_match = match_fn(line)

        if is_match:
            # Emit buffered before-context lines
            for buf_idx, buf_line in before_buf:
                if buf_idx not in emitted:
                    emitted.add(buf_idx)
                    yield (buf_idx, buf_line, False)

            if lineno not in emitted:
                emitted.add(lineno)
                yield (lineno, line, True)

            after_countdown = after
        elif after_countdown > 0:
            if lineno not in emitted:
                emitted.add(lineno)
                yield (lineno, line, False)
            after_countdown -= 1
        else:
            if before > 0:
                before_buf.append((lineno, line))


def collect_context_lines(
    lines: List[str],
    before: int = 0,
    after: int = 0,
    match_fn=None,
) -> List[Tuple[int, str, bool]]:
    """Return a list of (lineno, line, is_match) with context applied."""
    return list(iter_with_context(lines, before=before, after=after, match_fn=match_fn))
