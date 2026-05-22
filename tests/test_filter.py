"""Tests for logslice.filter module."""

import tempfile
import os
from datetime import datetime

import pytest

from logslice.filter import filter_lines, slice_file


SAMPLE_LINES = [
    "2024-01-10T08:00:00 INFO  server started",
    "2024-01-10T09:15:00 DEBUG request received from 192.168.1.1",
    "2024-01-10T10:30:00 ERROR disk full on /var/log",
    "2024-01-10T11:45:00 INFO  backup completed",
    "2024-01-10T12:00:00 WARN  memory usage at 90%",
]


class TestFilterLines:
    def test_no_filters_returns_all(self):
        result = list(filter_lines(iter(SAMPLE_LINES)))
        assert result == SAMPLE_LINES

    def test_start_filter(self):
        start = datetime(2024, 1, 10, 10, 0, 0)
        result = list(filter_lines(iter(SAMPLE_LINES), start=start))
        assert len(result) == 3
        assert all("10:30" in r or "11:45" in r or "12:00" in r for r in result)

    def test_end_filter(self):
        end = datetime(2024, 1, 10, 9, 30, 0)
        result = list(filter_lines(iter(SAMPLE_LINES), end=end))
        assert len(result) == 2
        assert "08:00" in result[0]
        assert "09:15" in result[1]

    def test_start_and_end_filter(self):
        start = datetime(2024, 1, 10, 9, 0, 0)
        end = datetime(2024, 1, 10, 11, 0, 0)
        result = list(filter_lines(iter(SAMPLE_LINES), start=start, end=end))
        assert len(result) == 2
        assert "09:15" in result[0]
        assert "10:30" in result[1]

    def test_pattern_filter(self):
        result = list(filter_lines(iter(SAMPLE_LINES), pattern="ERROR"))
        assert len(result) == 1
        assert "disk full" in result[0]

    def test_pattern_invert(self):
        result = list(filter_lines(iter(SAMPLE_LINES), pattern="INFO", invert=True))
        assert len(result) == 3
        assert all("INFO" not in r for r in result)

    def test_lines_without_timestamp_skipped_when_range_given(self):
        lines = ["no timestamp here", "2024-01-10T09:00:00 INFO ok"]
        start = datetime(2024, 1, 10, 8, 0, 0)
        result = list(filter_lines(iter(lines), start=start))
        assert result == ["2024-01-10T09:00:00 INFO ok"]

    def test_combined_time_and_pattern(self):
        start = datetime(2024, 1, 10, 9, 0, 0)
        result = list(filter_lines(iter(SAMPLE_LINES), start=start, pattern=r"\d{1,3}\.\d{1,3}"))
        assert len(result) == 1
        assert "192.168" in result[0]

    def test_strips_trailing_newline(self):
        lines = ["2024-01-10T08:00:00 INFO hello\n"]
        result = list(filter_lines(iter(lines)))
        assert result == ["2024-01-10T08:00:00 INFO hello"]


class TestSliceFile:
    def _write_temp(self, lines):
        fd, path = tempfile.mkstemp(suffix=".log")
        with os.fdopen(fd, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        return path

    def test_slice_file_basic(self):
        path = self._write_temp(SAMPLE_LINES)
        try:
            result = list(slice_file(path))
            assert len(result) == len(SAMPLE_LINES)
        finally:
            os.unlink(path)

    def test_slice_file_with_pattern(self):
        path = self._write_temp(SAMPLE_LINES)
        try:
            result = list(slice_file(path, pattern="WARN"))
            assert len(result) == 1
            assert "memory usage" in result[0]
        finally:
            os.unlink(path)
