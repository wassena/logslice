"""Tests for logslice.tail module."""

import threading
import time
import pytest

from logslice.tail import follow, tail_lines


@pytest.fixture
def log_file(tmp_path):
    log = tmp_path / "service.log"
    lines = [f"2024-01-01T10:00:{i:02d} INFO line {i}\n" for i in range(20)]
    log.write_text("".join(lines), encoding="utf-8")
    return str(log)


class TestTailLines:
    def test_returns_last_n_lines(self, log_file):
        result = tail_lines(log_file, n=5)
        assert len(result) == 5
        assert "line 19" in result[-1]

    def test_returns_all_when_n_exceeds_file(self, log_file):
        result = tail_lines(log_file, n=100)
        assert len(result) == 20

    def test_n_zero_returns_empty(self, log_file):
        assert tail_lines(log_file, n=0) == []

    def test_empty_file_returns_empty(self, tmp_path):
        empty = tmp_path / "empty.log"
        empty.write_text("", encoding="utf-8")
        assert tail_lines(str(empty), n=10) == []

    def test_single_line_file(self, tmp_path):
        log = tmp_path / "single.log"
        log.write_text("only line\n", encoding="utf-8")
        result = tail_lines(str(log), n=5)
        assert len(result) == 1
        assert "only line" in result[0]

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            tail_lines(str(tmp_path / "nope.log"), n=5)

    def test_default_n_is_ten(self, log_file):
        result = tail_lines(log_file)
        assert len(result) == 10


class TestFollow:
    def test_follow_yields_appended_lines(self, tmp_path):
        log = tmp_path / "growing.log"
        log.write_text("", encoding="utf-8")

        collected = []

        def writer():
            time.sleep(0.1)
            with open(str(log), "a") as f:
                f.write("new line 1\n")
                f.flush()
                time.sleep(0.1)
                f.write("new line 2\n")
                f.flush()

        t = threading.Thread(target=writer)
        t.start()

        for line in follow(str(log), poll_interval=0.05, max_wait=1.0):
            collected.append(line)
            if len(collected) >= 2:
                break

        t.join()
        assert len(collected) == 2
        assert "new line 1" in collected[0]
        assert "new line 2" in collected[1]

    def test_follow_stops_after_max_wait(self, tmp_path):
        log = tmp_path / "idle.log"
        log.write_text("", encoding="utf-8")
        result = list(follow(str(log), poll_interval=0.05, max_wait=0.2))
        assert result == []
