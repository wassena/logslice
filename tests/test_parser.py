"""Tests for logslice.parser module."""

import pytest
from datetime import datetime
from logslice.parser import extract_timestamp, matches_pattern, parse_line


class TestExtractTimestamp:
    def test_iso8601_with_microseconds(self):
        line = "2024-03-15T12:34:56.789000 ERROR something failed"
        ts = extract_timestamp(line)
        assert ts is not None
        assert ts.year == 2024
        assert ts.month == 3
        assert ts.day == 15
        assert ts.hour == 12

    def test_iso8601_basic(self):
        line = "2024-01-01 00:00:00 INFO server started"
        ts = extract_timestamp(line)
        assert ts is not None
        assert ts.year == 2024

    def test_apache_format(self):
        line = '127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200'
        ts = extract_timestamp(line)
        assert ts is not None
        assert ts.day == 10
        assert ts.hour == 13

    def test_no_timestamp_returns_none(self):
        line = "no timestamp here just plain text"
        assert extract_timestamp(line) is None

    def test_empty_line(self):
        assert extract_timestamp("") is None


class TestMatchesPattern:
    def test_simple_substring_match(self):
        assert matches_pattern("ERROR: disk full", "ERROR")

    def test_case_insensitive_by_default(self):
        assert matches_pattern("error: disk full", "ERROR")

    def test_case_sensitive_no_match(self):
        assert not matches_pattern("error: disk full", "ERROR", case_sensitive=True)

    def test_regex_pattern(self):
        assert matches_pattern("request took 250ms", r"\d+ms")

    def test_invalid_regex_falls_back_to_substring(self):
        assert matches_pattern("price is [high]", "[high]")

    def test_no_match(self):
        assert not matches_pattern("INFO: all good", "CRITICAL")


class TestParseLine:
    def test_returns_dict_with_keys(self):
        result = parse_line("2024-06-01 10:00:00 DEBUG init\n")
        assert "raw" in result
        assert "timestamp" in result

    def test_strips_newline_from_raw(self):
        result = parse_line("some log line\n")
        assert not result["raw"].endswith("\n")

    def test_timestamp_parsed_correctly(self):
        result = parse_line("2024-06-01 10:00:00 DEBUG init")
        assert isinstance(result["timestamp"], datetime)

    def test_no_timestamp_in_line(self):
        result = parse_line("plain text with no date")
        assert result["timestamp"] is None
