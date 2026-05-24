"""Tests for logslice.cli module."""

import os
import tempfile
import pytest

from logslice.cli import build_parser, run


SAMPLE_LOG = """\
2024-01-15T10:00:00 INFO  Server started
2024-01-15T10:01:00 DEBUG Request received
2024-01-15T10:02:00 ERROR Something failed
2024-01-15T10:03:00 INFO  Request completed
"""


@pytest.fixture()
def log_file(tmp_path):
    path = tmp_path / "app.log"
    path.write_text(SAMPLE_LOG)
    return str(path)


class TestBuildParser:
    def test_default_args(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.file is None
        assert args.start is None
        assert args.end is None
        assert args.pattern is None
        assert args.line_numbers is False
        assert args.count is False

    def test_all_flags(self):
        parser = build_parser()
        args = parser.parse_args([
            "myfile.log", "-s", "10:00", "-e", "11:00",
            "-p", "ERROR", "-n", "-c", "--color", "--summary",
        ])
        assert args.file == "myfile.log"
        assert args.start == "10:00"
        assert args.end == "11:00"
        assert args.pattern == "ERROR"
        assert args.line_numbers is True
        assert args.count is True
        assert args.color is True
        assert args.summary is True


class TestRun:
    def test_returns_zero_on_success(self, log_file, capsys):
        exit_code = run([log_file])
        assert exit_code == 0

    def test_outputs_all_lines_no_filters(self, log_file, capsys):
        run([log_file])
        captured = capsys.readouterr()
        assert "Server started" in captured.out
        assert "Something failed" in captured.out

    def test_pattern_filter(self, log_file, capsys):
        run([log_file, "-p", "ERROR"])
        captured = capsys.readouterr()
        assert "ERROR" in captured.out
        assert "DEBUG" not in captured.out

    def test_count_only(self, log_file, capsys):
        run([log_file, "-c"])
        captured = capsys.readouterr()
        assert captured.out.strip() == "4"

    def test_missing_file_returns_one(self, capsys):
        exit_code = run(["nonexistent_file.log"])
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "error" in captured.err.lower()

    def test_line_numbers_in_output(self, log_file, capsys):
        run([log_file, "-n"])
        captured = capsys.readouterr()
        assert "1:" in captured.out
