"""Tests for logslice.stats module."""

from datetime import datetime

import pytest

from logslice.stats import SliceStats, format_stats


class TestSliceStats:
    def test_initial_state(self):
        s = SliceStats()
        assert s.total_lines == 0
        assert s.matched_lines == 0
        assert s.skipped_lines == 0
        assert s.first_matched_ts is None
        assert s.last_matched_ts is None

    def test_record_matched_line(self):
        s = SliceStats()
        s.record_line(matched=True)
        assert s.total_lines == 1
        assert s.matched_lines == 1
        assert s.skipped_lines == 0

    def test_record_skipped_line(self):
        s = SliceStats()
        s.record_line(matched=False)
        assert s.total_lines == 1
        assert s.matched_lines == 0
        assert s.skipped_lines == 1

    def test_match_rate_zero_when_no_lines(self):
        s = SliceStats()
        assert s.match_rate == 0.0

    def test_match_rate_calculation(self):
        s = SliceStats()
        s.record_line(matched=True)
        s.record_line(matched=False)
        assert s.match_rate == pytest.approx(0.5)

    def test_timestamps_tracked(self):
        s = SliceStats()
        t1 = datetime(2024, 1, 1, 10, 0, 0)
        t2 = datetime(2024, 1, 1, 11, 0, 0)
        s.record_line(matched=True, timestamp=t1)
        s.record_line(matched=True, timestamp=t2)
        assert s.first_matched_ts == t1
        assert s.last_matched_ts == t2

    def test_timestamp_not_updated_on_skip(self):
        s = SliceStats()
        t = datetime(2024, 1, 1, 10, 0, 0)
        s.record_line(matched=False, timestamp=t)
        assert s.first_matched_ts is None

    def test_pattern_counts(self):
        s = SliceStats()
        s.record_line(matched=True, pattern="ERROR")
        s.record_line(matched=True, pattern="ERROR")
        s.record_line(matched=True, pattern="WARN")
        assert s.patterns_matched["ERROR"] == 2
        assert s.patterns_matched["WARN"] == 1

    def test_elapsed_seconds(self):
        s = SliceStats()
        s.start_time = datetime(2024, 1, 1, 10, 0, 0)
        s.end_time = datetime(2024, 1, 1, 10, 0, 2)
        assert s.elapsed_seconds == pytest.approx(2.0)

    def test_elapsed_seconds_none_when_missing(self):
        s = SliceStats()
        assert s.elapsed_seconds is None


class TestFormatStats:
    def test_basic_output_contains_counts(self):
        s = SliceStats()
        s.record_line(matched=True)
        s.record_line(matched=False)
        output = format_stats(s)
        assert "Total lines processed : 2" in output
        assert "Matched lines         : 1" in output
        assert "Skipped lines         : 1" in output
        assert "50.0%" in output

    def test_timestamp_lines_present(self):
        s = SliceStats()
        ts = datetime(2024, 6, 15, 8, 30, 0)
        s.record_line(matched=True, timestamp=ts)
        output = format_stats(s)
        assert "2024-06-15T08:30:00" in output

    def test_pattern_section_present(self):
        s = SliceStats()
        s.record_line(matched=True, pattern="ERROR")
        output = format_stats(s)
        assert "Pattern hit counts" in output
        assert "'ERROR': 1" in output

    def test_no_pattern_section_when_empty(self):
        s = SliceStats()
        s.record_line(matched=True)
        output = format_stats(s)
        assert "Pattern hit counts" not in output
