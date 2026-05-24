"""Tests for logslice.sampler."""

import pytest

from logslice.sampler import (
    count_sampled,
    sample_by_interval,
    sample_by_rate,
)

LINES = [f"line {i}\n" for i in range(1, 101)]  # 100 lines


class TestSampleByRate:
    def test_rate_one_returns_all(self):
        result = list(sample_by_rate(LINES, rate=1.0, seed=0))
        assert result == LINES

    def test_rate_zero_raises(self):
        with pytest.raises(ValueError, match="rate must be in"):
            list(sample_by_rate(LINES, rate=0.0))

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError):
            list(sample_by_rate(LINES, rate=-0.5))

    def test_rate_above_one_raises(self):
        with pytest.raises(ValueError):
            list(sample_by_rate(LINES, rate=1.1))

    def test_approximate_fraction_kept(self):
        result = list(sample_by_rate(LINES, rate=0.5, seed=42))
        # With seed=42 and 100 lines at 50% we expect roughly 40-60
        assert 30 <= len(result) <= 70

    def test_seed_gives_reproducible_output(self):
        r1 = list(sample_by_rate(LINES, rate=0.3, seed=7))
        r2 = list(sample_by_rate(LINES, rate=0.3, seed=7))
        assert r1 == r2

    def test_different_seeds_differ(self):
        r1 = list(sample_by_rate(LINES, rate=0.5, seed=1))
        r2 = list(sample_by_rate(LINES, rate=0.5, seed=2))
        assert r1 != r2

    def test_empty_input_returns_empty(self):
        assert list(sample_by_rate([], rate=1.0)) == []


class TestSampleByInterval:
    def test_interval_one_returns_all(self):
        result = list(sample_by_interval(LINES, interval=1))
        assert result == LINES

    def test_interval_two_returns_half(self):
        result = list(sample_by_interval(LINES, interval=2))
        assert len(result) == 50
        assert result[0] == "line 1\n"
        assert result[1] == "line 6\n"

    def test_interval_ten(self):
        result = list(sample_by_interval(LINES, interval=10))
        assert len(result) == 10
        assert result[0] == "line 1\n"
        assert result[-1] == "line 91\n"

    def test_interval_larger_than_input(self):
        result = list(sample_by_interval(["only\n"], interval=100))
        assert result == ["only\n"]

    def test_interval_zero_raises(self):
        with pytest.raises(ValueError, match="interval must be >= 1"):
            list(sample_by_interval(LINES, interval=0))

    def test_negative_interval_raises(self):
        with pytest.raises(ValueError):
            list(sample_by_interval(LINES, interval=-3))

    def test_empty_input_returns_empty(self):
        assert list(sample_by_interval([], interval=5)) == []


class TestCountSampled:
    def test_count_matches_list_length(self):
        rate = 0.4
        seed = 99
        expected = len(list(sample_by_rate(LINES, rate=rate, seed=seed)))
        assert count_sampled(LINES, rate=rate, seed=seed) == expected

    def test_count_rate_one(self):
        assert count_sampled(LINES, rate=1.0) == 100
