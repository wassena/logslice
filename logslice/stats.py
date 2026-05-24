"""Statistics collection and reporting for log slicing operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SliceStats:
    """Holds statistics gathered during a log slice operation."""

    total_lines: int = 0
    matched_lines: int = 0
    skipped_lines: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    first_matched_ts: Optional[datetime] = None
    last_matched_ts: Optional[datetime] = None
    patterns_matched: dict = field(default_factory=dict)

    def record_line(self, matched: bool, timestamp: Optional[datetime] = None, pattern: Optional[str] = None) -> None:
        """Record a single line processed during filtering."""
        self.total_lines += 1
        if matched:
            self.matched_lines += 1
            if timestamp is not None:
                if self.first_matched_ts is None:
                    self.first_matched_ts = timestamp
                self.last_matched_ts = timestamp
            if pattern:
                self.patterns_matched[pattern] = self.patterns_matched.get(pattern, 0) + 1
        else:
            self.skipped_lines += 1

    @property
    def match_rate(self) -> float:
        """Return the fraction of lines that matched, or 0.0 if no lines processed."""
        if self.total_lines == 0:
            return 0.0
        return self.matched_lines / self.total_lines

    @property
    def elapsed_seconds(self) -> Optional[float]:
        """Return elapsed wall-clock seconds if both start and end times are set."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


def format_stats(stats: SliceStats) -> str:
    """Return a human-readable summary string for the given SliceStats."""
    lines = [
        f"Total lines processed : {stats.total_lines}",
        f"Matched lines         : {stats.matched_lines}",
        f"Skipped lines         : {stats.skipped_lines}",
        f"Match rate            : {stats.match_rate:.1%}",
    ]
    if stats.first_matched_ts:
        lines.append(f"First matched ts      : {stats.first_matched_ts.isoformat()}")
    if stats.last_matched_ts:
        lines.append(f"Last matched ts       : {stats.last_matched_ts.isoformat()}")
    if stats.elapsed_seconds is not None:
        lines.append(f"Elapsed               : {stats.elapsed_seconds:.3f}s")
    if stats.patterns_matched:
        lines.append("Pattern hit counts    :")
        for pat, count in sorted(stats.patterns_matched.items()):
            lines.append(f"  {pat!r}: {count}")
    return "\n".join(lines)
