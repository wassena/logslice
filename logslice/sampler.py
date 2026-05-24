"""Line sampling utilities for logslice.

Provides rate-based and interval-based sampling to reduce output volume
when working with very large log files.
"""

from __future__ import annotations

import random
from typing import Iterable, Iterator


def sample_by_rate(
    lines: Iterable[str],
    rate: float,
    seed: int | None = None,
) -> Iterator[str]:
    """Yield lines randomly sampled at the given rate (0.0 < rate <= 1.0).

    Args:
        lines: Input lines to sample from.
        rate: Fraction of lines to keep, e.g. 0.1 keeps ~10%.
        seed: Optional random seed for reproducibility.

    Raises:
        ValueError: If rate is not in the range (0, 1].
    """
    if not (0.0 < rate <= 1.0):
        raise ValueError(f"rate must be in (0, 1], got {rate!r}")

    rng = random.Random(seed)
    for line in lines:
        if rng.random() < rate:
            yield line


def sample_by_interval(
    lines: Iterable[str],
    interval: int,
) -> Iterator[str]:
    """Yield every *interval*-th line (1-based index).

    Args:
        lines: Input lines to sample from.
        interval: Keep every nth line; e.g. 5 keeps lines 1, 6, 11, …

    Raises:
        ValueError: If interval is less than 1.
    """
    if interval < 1:
        raise ValueError(f"interval must be >= 1, got {interval!r}")

    for index, line in enumerate(lines, start=1):
        if index % interval == 1:
            yield line


def count_sampled(lines: Iterable[str], rate: float, seed: int | None = None) -> int:
    """Return the number of lines that would survive rate-based sampling."""
    return sum(1 for _ in sample_by_rate(lines, rate, seed=seed))
