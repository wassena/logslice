"""Command-line interface for logslice."""

import argparse
import sys
from typing import Optional

from logslice.reader import open_log_file, iter_lines
from logslice.filter import filter_lines
from logslice.context import collect_context_lines
from logslice.highlighter import highlight_pattern
from logslice.output import format_line, write_lines, write_summary
from logslice.stats import SliceStats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Fast log filtering and slicing tool.",
    )
    parser.add_argument("file", help="Log file to process (plain or gzipped)")
    parser.add_argument("--start", help="Start timestamp (ISO8601 or Apache format)")
    parser.add_argument("--end", help="End timestamp (ISO8601 or Apache format)")
    parser.add_argument("--pattern", "-p", help="Regex pattern to filter lines")
    parser.add_argument("--before", "-B", type=int, default=0,
                        help="Lines of context before each match")
    parser.add_argument("--after", "-A", type=int, default=0,
                        help="Lines of context after each match")
    parser.add_argument("--context", "-C", type=int, default=None,
                        help="Lines of context before AND after each match")
    parser.add_argument("--colorize", action="store_true",
                        help="Colorize matched patterns in output")
    parser.add_argument("--line-numbers", "-n", action="store_true",
                        help="Show line numbers")
    parser.add_argument("--summary", action="store_true",
                        help="Print summary statistics after output")
    return parser


def run(args: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    before = args.before
    after = args.after
    if args.context is not None:
        before = after = args.context

    stats = SliceStats()
    stats.start_timer()

    try:
        with open_log_file(args.file) as fh:
            raw_lines = list(iter_lines(fh))
    except (OSError, IOError) as exc:
        print(f"logslice: error opening file: {exc}", file=sys.stderr)
        return 1

    filtered = filter_lines(
        raw_lines,
        start=getattr(args, "start", None),
        end=getattr(args, "end", None),
        pattern=getattr(args, "pattern", None),
        stats=stats,
    )

    use_context = before > 0 or after > 0
    if use_context and args.pattern:
        from logslice.parser import matches_pattern
        match_fn = lambda line: matches_pattern(line, args.pattern)
        context_results = collect_context_lines(
            filtered, before=before, after=after, match_fn=match_fn
        )
        output_lines = [
            format_line(line, lineno=lineno if args.line_numbers else None,
                        colorize=args.colorize and is_match,
                        pattern=args.pattern if args.colorize else None)
            for lineno, line, is_match in context_results
        ]
    else:
        output_lines = [
            format_line(line, lineno=i + 1 if args.line_numbers else None,
                        colorize=args.colorize,
                        pattern=getattr(args, "pattern", None))
            for i, line in enumerate(filtered)
        ]

    write_lines(output_lines, out=out)

    stats.stop_timer()
    if args.summary:
        write_summary(stats, out=out)

    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
