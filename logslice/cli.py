"""Command-line interface for logslice."""

import argparse
import sys
from typing import List, Optional

from logslice.filter import slice_file
from logslice.output import write_lines, write_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Fast log filtering and slicing tool with time-range and pattern support.",
    )
    parser.add_argument("file", nargs="?", help="Log file to process (default: stdin)")
    parser.add_argument("-s", "--start", metavar="DATETIME", help="Start of time range (inclusive)")
    parser.add_argument("-e", "--end", metavar="DATETIME", help="End of time range (inclusive)")
    parser.add_argument("-p", "--pattern", metavar="REGEX", help="Filter lines matching regex pattern")
    parser.add_argument("-n", "--line-numbers", action="store_true", help="Prefix output with line numbers")
    parser.add_argument("-c", "--count", action="store_true", help="Print only the count of matching lines")
    parser.add_argument("--color", action="store_true", help="Colorize line number prefixes")
    parser.add_argument("--summary", action="store_true", help="Print match summary to stderr")
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    """Entry point for the CLI. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.file:
            lines = slice_file(
                args.file,
                start=args.start,
                end=args.end,
                pattern=args.pattern,
            )
        else:
            from logslice.filter import filter_lines
            lines = filter_lines(
                sys.stdin,
                start=args.start,
                end=args.end,
                pattern=args.pattern,
            )

        count = write_lines(
            lines,
            output=sys.stdout,
            line_numbers=args.line_numbers,
            colorize=args.color,
            count_only=args.count,
        )

        if args.summary:
            write_summary(count)

    except FileNotFoundError as exc:
        sys.stderr.write(f"logslice: error: {exc}\n")
        return 1
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"logslice: unexpected error: {exc}\n")
        return 2

    return 0


def main() -> None:
    sys.exit(run())
