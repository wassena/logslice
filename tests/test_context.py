"""Tests for logslice.context module."""

import pytest
from logslice.context import iter_with_context, collect_context_lines


LINES = [
    "2024-01-01 INFO  starting up\n",
    "2024-01-01 DEBUG init config\n",
    "2024-01-01 ERROR something broke\n",
    "2024-01-01 DEBUG cleanup\n",
    "2024-01-01 INFO  shutting down\n",
]


def is_error(line: str) -> bool:
    return "ERROR" in line


def is_info(line: str) -> bool:
    return "INFO" in line


class TestCollectContextLines:
    def test_no_context_returns_only_matches(self):
        result = collect_context_lines(LINES, match_fn=is_error)
        assert len(result) == 1
        lineno, line, is_match = result[0]
        assert lineno == 3
        assert is_match is True
        assert "ERROR" in line

    def test_before_context_includes_preceding_lines(self):
        result = collect_context_lines(LINES, before=2, match_fn=is_error)
        assert len(result) == 3
        linenos = [r[0] for r in result]
        assert linenos == [1, 2, 3]
        assert result[2][2] is True   # match
        assert result[0][2] is False  # context
        assert result[1][2] is False  # context

    def test_after_context_includes_following_lines(self):
        result = collect_context_lines(LINES, after=1, match_fn=is_error)
        assert len(result) == 2
        linenos = [r[0] for r in result]
        assert linenos == [3, 4]
        assert result[0][2] is True
        assert result[1][2] is False

    def test_before_and_after_context(self):
        result = collect_context_lines(LINES, before=1, after=1, match_fn=is_error)
        linenos = [r[0] for r in result]
        assert linenos == [2, 3, 4]

    def test_no_duplicates_with_overlapping_context(self):
        result = collect_context_lines(LINES, before=2, after=2, match_fn=is_info)
        linenos = [r[0] for r in result]
        # lines 1,2,3,4,5 should each appear once
        assert len(linenos) == len(set(linenos))

    def test_no_match_fn_returns_all_lines(self):
        result = collect_context_lines(LINES)
        assert len(result) == len(LINES)
        assert all(is_match for _, _, is_match in result)

    def test_empty_lines_returns_empty(self):
        result = collect_context_lines([], before=2, after=2, match_fn=is_error)
        assert result == []

    def test_before_exceeds_file_start(self):
        result = collect_context_lines(LINES, before=10, match_fn=is_error)
        linenos = [r[0] for r in result]
        assert 1 in linenos
        assert 3 in linenos

    def test_after_exceeds_file_end(self):
        result = collect_context_lines(LINES, after=10, match_fn=is_error)
        linenos = [r[0] for r in result]
        assert 3 in linenos
        assert 5 in linenos

    def test_line_numbers_are_one_based(self):
        result = collect_context_lines(LINES, match_fn=is_error)
        assert result[0][0] == 3  # third line
