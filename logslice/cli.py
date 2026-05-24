"""Command-line interface for logslice."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from logslice.filter import slice_file
from logslice.output import write_lines, write_summary
from logslice.reader import open_log_file, iter_lines
from logslice.sampler import sample_by_rate, sample_by_interval
from logslice.stats import SliceStats


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Fast log filtering and slicing tool with time-range and pattern support.",
    )
    p.add_argument("file", nargs="?", help="Log file to process (default: stdin)")
    p.add_argument("--start", metavar="DATETIME", help="Include lines at or after this timestamp")
    p.add_argument("--end", metavar="DATETIME", help="Include lines at or before this timestamp")
    p.add_argument("-p", "--pattern", metavar="PATTERN", help="Regex pattern to filter lines")
    p.add_argument("-n", "--line-numbers", action="store_true", help="Prefix output with line numbers")
    p.add_argument("--color", action="store_true", help="Colorize matched patterns")
    p.add_argument("--summary", action="store_true", help="Print summary statistics after output")
    # Sampling flags
    p.add_argument(
        "--sample-rate",
        type=float,
        metavar="RATE",
        help="Keep only a random fraction of lines, e.g. 0.1 for 10%%",
    )
    p.add_argument(
        "--sample-interval",
        type=int,
        metavar="N",
        help="Keep every Nth line from the filtered output",
    )
    return p


def run(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    """Execute the slice operation and return an exit code."""
    stats = SliceStats()

    if args.file:
        fh = open_log_file(Path(args.file))
    else:
        fh = sys.stdin

    try:
        lines = iter_lines(fh)
        filtered = slice_file(
            lines,
            start=args.start,
            end=args.end,
            pattern=getattr(args, "pattern", None),
            stats=stats,
        )

        # Apply optional sampling
        if getattr(args, "sample_rate", None) is not None:
            try:
                filtered = sample_by_rate(filtered, rate=args.sample_rate)
            except ValueError as exc:
                err.write(f"logslice: error: {exc}\n")
                return 2

        if getattr(args, "sample_interval", None) is not None:
            try:
                filtered = sample_by_interval(filtered, interval=args.sample_interval)
            except ValueError as exc:
                err.write(f"logslice: error: {exc}\n")
                return 2

        write_lines(
            filtered,
            out=out,
            line_numbers=getattr(args, "line_numbers", False),
            colorize=getattr(args, "color", False),
            pattern=getattr(args, "pattern", None),
        )

        if getattr(args, "summary", False):
            write_summary(stats, out=err)
    finally:
        if args.file:
            fh.close()

    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    sys.exit(run(args))


if __name__ == "__main__":
    main()
