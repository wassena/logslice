"""Tests for logslice.output module."""

import io
import pytest

from logslice.output import format_line, write_lines, write_summary


SAMPLE_LINES = [
    "2024-01-15T10:00:00 INFO  Server started\n",
    "2024-01-15T10:01:00 DEBUG Request received\n",
    "2024-01-15T10:02:00 ERROR Something failed\n",
]


class TestFormatLine:
    def test_plain_line_strips_newline(self):
        result = format_line("hello world\n")
        assert result == "hello world"

    def test_with_line_number(self):
        result = format_line("hello\n", line_number=42)
        assert "42" in result
        assert "hello" in result

    def test_without_line_number(self):
        result = format_line("hello\n", line_number=None)
        assert result == "hello"

    def test_colorize_adds_escape_codes(self):
        result = format_line("hello\n", line_number=1, colorize=True)
        assert "\033[" in result
        assert "hello" in result

    def test_no_colorize_no_escape_codes(self):
        result = format_line("hello\n", line_number=1, colorize=False)
        assert "\033[" not in result


class TestWriteLines:
    def test_writes_all_lines(self):
        buf = io.StringIO()
        count = write_lines(iter(SAMPLE_LINES), output=buf)
        assert count == 3
        output = buf.getvalue()
        assert "Server started" in output
        assert "Request received" in output
        assert "Something failed" in output

    def test_count_only_does_not_write_lines(self):
        buf = io.StringIO()
        count = write_lines(iter(SAMPLE_LINES), output=buf, count_only=True)
        assert count == 3
        assert buf.getvalue().strip() == "3"
        assert "INFO" not in buf.getvalue()

    def test_line_numbers_in_output(self):
        buf = io.StringIO()
        write_lines(iter(SAMPLE_LINES), output=buf, line_numbers=True)
        lines = buf.getvalue().splitlines()
        assert lines[0].lstrip().startswith("1:")
        assert lines[1].lstrip().startswith("2:")

    def test_empty_input_returns_zero(self):
        buf = io.StringIO()
        count = write_lines(iter([]), output=buf)
        assert count == 0
        assert buf.getvalue() == ""

    def test_returns_correct_count(self):
        buf = io.StringIO()
        count = write_lines(iter(SAMPLE_LINES[:2]), output=buf)
        assert count == 2


class TestWriteSummary:
    def test_singular_line(self):
        buf = io.StringIO()
        write_summary(1, output=buf)
        assert "1 matching line" in buf.getvalue()

    def test_plural_lines(self):
        buf = io.StringIO()
        write_summary(5, output=buf)
        assert "5 matching lines" in buf.getvalue()

    def test_zero_lines(self):
        buf = io.StringIO()
        write_summary(0, output=buf)
        assert "0 matching lines" in buf.getvalue()
