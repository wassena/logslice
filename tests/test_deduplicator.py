"""Tests for logslice.deduplicator."""

import pytest
from logslice.deduplicator import deduplicate_lines, count_duplicates, _line_key


LINES_WITH_DUPES = [
    "2024-01-01 10:00:00 ERROR disk full\n",
    "2024-01-01 10:00:01 INFO  heartbeat\n",
    "2024-01-01 10:00:02 ERROR disk full\n",  # duplicate of line 0
    "2024-01-01 10:00:03 INFO  heartbeat\n",  # duplicate of line 1
    "2024-01-01 10:00:04 WARN  cpu high\n",
]


class TestDeduplicateLines:
    def test_no_duplicates_returns_all(self):
        lines = ["line one\n", "line two\n", "line three\n"]
        result = list(deduplicate_lines(lines))
        assert result == lines

    def test_exact_duplicates_removed(self):
        lines = ["same line\n", "same line\n", "different\n"]
        result = list(deduplicate_lines(lines))
        assert result == ["same line\n", "different\n"]

    def test_all_duplicates_yields_one(self):
        lines = ["repeat\n"] * 5
        result = list(deduplicate_lines(lines))
        assert result == ["repeat\n"]

    def test_empty_input_returns_empty(self):
        assert list(deduplicate_lines([])) == []

    def test_order_preserved(self):
        lines = ["b\n", "a\n", "c\n", "a\n", "b\n"]
        result = list(deduplicate_lines(lines))
        assert result == ["b\n", "a\n", "c\n"]

    def test_ignore_timestamps_deduplicates_same_message(self):
        result = list(deduplicate_lines(LINES_WITH_DUPES, ignore_timestamps=True))
        # Only 3 unique messages: ERROR disk full, INFO heartbeat, WARN cpu high
        assert len(result) == 3

    def test_ignore_timestamps_false_keeps_all_different_timestamps(self):
        result = list(deduplicate_lines(LINES_WITH_DUPES, ignore_timestamps=False))
        # Without timestamp stripping, all 5 lines are distinct strings
        assert len(result) == 5

    def test_max_cache_evicts_old_entries(self):
        # Fill cache beyond max_cache; evicted keys can reappear
        lines = [f"line {i}\n" for i in range(5)] + ["line 0\n"]
        result = list(deduplicate_lines(lines, max_cache=3))
        # "line 0" was evicted from cache, so it appears twice
        assert result.count("line 0\n") == 2


class TestCountDuplicates:
    def test_returns_total_and_unique(self):
        lines = ["a\n", "b\n", "a\n", "c\n"]
        total, unique = count_duplicates(lines)
        assert total == 4
        assert unique == 3

    def test_empty_returns_zeros(self):
        assert count_duplicates([]) == (0, 0)

    def test_all_unique(self):
        lines = ["x\n", "y\n", "z\n"]
        total, unique = count_duplicates(lines)
        assert total == unique == 3

    def test_ignore_timestamps_reduces_unique_count(self):
        total, unique = count_duplicates(LINES_WITH_DUPES, ignore_timestamps=True)
        assert total == 5
        assert unique == 3
