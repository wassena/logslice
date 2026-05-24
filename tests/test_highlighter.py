"""Tests for logslice.highlighter module."""

import pytest
from logslice.highlighter import (
    highlight_pattern,
    highlight_multiple,
    strip_ansi,
    ANSI_RESET,
    ANSI_BOLD_YELLOW,
    ANSI_BOLD_RED,
    ANSI_BOLD_CYAN,
)


class TestHighlightPattern:
    def test_basic_match_is_wrapped(self):
        result = highlight_pattern("error occurred", "error")
        assert ANSI_BOLD_YELLOW in result
        assert ANSI_RESET in result
        assert "error" in result

    def test_no_match_returns_original(self):
        result = highlight_pattern("info message", "error")
        assert result == "info message"

    def test_empty_pattern_returns_original(self):
        line = "some log line"
        assert highlight_pattern(line, "") == line

    def test_custom_color_is_used(self):
        result = highlight_pattern("warning here", "warning", ANSI_BOLD_RED)
        assert ANSI_BOLD_RED in result
        assert ANSI_BOLD_YELLOW not in result

    def test_case_insensitive_match(self):
        result = highlight_pattern("ERROR in system", "error")
        assert ANSI_BOLD_YELLOW in result
        plain = strip_ansi(result)
        assert plain == "ERROR in system"

    def test_multiple_occurrences_highlighted(self):
        result = highlight_pattern("err and another err", "err")
        # Each occurrence adds color + reset pair
        assert result.count(ANSI_RESET) == 2

    def test_invalid_regex_falls_back_to_literal(self):
        # Pattern with unbalanced bracket is invalid regex
        result = highlight_pattern("value[0", "[0")
        assert ANSI_BOLD_YELLOW in result
        plain = strip_ansi(result)
        assert plain == "value[0"

    def test_regex_pattern_works(self):
        result = highlight_pattern("2024-01-15 info", r"\d{4}-\d{2}-\d{2}")
        assert ANSI_BOLD_YELLOW in result
        plain = strip_ansi(result)
        assert plain == "2024-01-15 info"


class TestHighlightMultiple:
    def test_two_patterns_use_different_colors(self):
        result = highlight_multiple("error and warning", ["error", "warning"])
        assert ANSI_BOLD_YELLOW in result
        assert ANSI_BOLD_RED in result

    def test_three_patterns_cycle_colors(self):
        result = highlight_multiple("a b c", ["a", "b", "c"])
        assert ANSI_BOLD_YELLOW in result
        assert ANSI_BOLD_RED in result
        assert ANSI_BOLD_CYAN in result

    def test_empty_patterns_list_returns_original(self):
        line = "unchanged line"
        assert highlight_multiple(line, []) == line

    def test_plain_text_preserved(self):
        result = highlight_multiple("foo bar", ["foo", "bar"])
        plain = strip_ansi(result)
        assert plain == "foo bar"


class TestStripAnsi:
    def test_removes_color_codes(self):
        colored = f"{ANSI_BOLD_YELLOW}hello{ANSI_RESET}"
        assert strip_ansi(colored) == "hello"

    def test_plain_text_unchanged(self):
        assert strip_ansi("plain text") == "plain text"

    def test_multiple_codes_removed(self):
        text = f"{ANSI_BOLD_RED}err{ANSI_RESET} and {ANSI_BOLD_CYAN}info{ANSI_RESET}"
        assert strip_ansi(text) == "err and info"
