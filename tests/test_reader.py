"""Tests for logslice.reader module."""

import gzip
import os
import pytest

from logslice.reader import (
    count_lines,
    detect_encoding,
    is_gzipped,
    iter_lines,
    open_log_file,
)


@pytest.fixture
def plain_log(tmp_path):
    log = tmp_path / "app.log"
    log.write_text(
        "2024-01-01T10:00:00 INFO started\n"
        "2024-01-01T10:00:01 DEBUG processing\n"
        "2024-01-01T10:00:02 ERROR failed\n",
        encoding="utf-8",
    )
    return str(log)


@pytest.fixture
def gzip_log(tmp_path):
    log = tmp_path / "app.log.gz"
    with gzip.open(str(log), "wt", encoding="utf-8") as f:
        f.write("2024-01-01T10:00:00 INFO gzip line one\n")
        f.write("2024-01-01T10:00:01 INFO gzip line two\n")
    return str(log)


class TestIsGzipped:
    def test_plain_file_returns_false(self, plain_log):
        assert is_gzipped(plain_log) is False

    def test_gzip_file_returns_true(self, gzip_log):
        assert is_gzipped(gzip_log) is True

    def test_missing_file_returns_false(self, tmp_path):
        assert is_gzipped(str(tmp_path / "missing.log")) is False


class TestDetectEncoding:
    def test_utf8_file(self, plain_log):
        enc = detect_encoding(plain_log)
        assert enc in ("utf-8", "ascii")

    def test_latin1_file(self, tmp_path):
        log = tmp_path / "latin.log"
        log.write_bytes(b"caf\xe9 au lait\n")
        enc = detect_encoding(str(log))
        assert enc == "latin-1"


class TestIterLines:
    def test_yields_correct_line_count(self, plain_log):
        lines = list(iter_lines(plain_log))
        assert len(lines) == 3

    def test_line_numbers_start_at_one(self, plain_log):
        lines = list(iter_lines(plain_log))
        assert lines[0][0] == 1
        assert lines[2][0] == 3

    def test_line_content_is_correct(self, plain_log):
        lines = list(iter_lines(plain_log))
        assert "INFO started" in lines[0][2]
        assert "ERROR failed" in lines[2][2]

    def test_gzip_file_readable(self, gzip_log):
        lines = list(iter_lines(gzip_log))
        assert len(lines) == 2
        assert "gzip line one" in lines[0][2]

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            list(iter_lines(str(tmp_path / "nope.log")))


class TestCountLines:
    def test_plain_file_count(self, plain_log):
        assert count_lines(plain_log) == 3

    def test_gzip_file_count(self, gzip_log):
        assert count_lines(gzip_log) == 2

    def test_empty_file(self, tmp_path):
        empty = tmp_path / "empty.log"
        empty.write_text("", encoding="utf-8")
        assert count_lines(str(empty)) == 0
