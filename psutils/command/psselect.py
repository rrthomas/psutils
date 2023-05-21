import importlib.metadata
import argparse
import sys
import warnings
from typing import List

from psutils.argparse import HelpFormatter, add_basic_arguments
from psutils.command.pstops import pstops
from psutils.warnings import die, simple_warning

VERSION = importlib.metadata.version("psutils")

VERSION_BANNER = f"""\
%(prog)s {VERSION}
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""


def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Select pages from a PDF or PostScript document.",
        formatter_class=HelpFormatter,
        usage="%(prog)s [OPTION...] [PAGES] [INFILE [OUTFILE]]",
        add_help=False,
        epilog="""
PAGES is a comma-separated list of pages and page ranges; see
pstops(1) for more details.
""",
    )
    warnings.showwarning = simple_warning(parser.prog)

    # Command-line parser
    parser.add_argument("-R", "-p", "--pages", help="select the given page ranges")
    parser.add_argument(
        "-e", "--even", action="store_true", help="select even-numbered output pages"
    )
    parser.add_argument(
        "-o", "--odd", action="store_true", help="select odd-numbered output pages"
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="reverse the order of the output pages",
    )
    parser.add_argument("alt_pages", metavar="PAGES", nargs="?", help=argparse.SUPPRESS)
    add_basic_arguments(parser, VERSION_BANNER)

    return parser


# pylint: disable=dangerous-default-value
def psselect(argv: List[str] = sys.argv[1:]) -> None:
    args = get_parser().parse_intermixed_args(argv)

    # Rearrange the pages
    cmd = []
    if not args.verbose:
        cmd.append("--quiet")
    if args.reverse:
        cmd.append("-r")
    if args.even:
        cmd.append("-e")
    if args.odd:
        cmd.append("-o")
    if args.alt_pages is not None:
        if (
            args.pages is None
            and args.even is False
            and args.odd is False
            and args.reverse is False
        ):
            args.pages = args.alt_pages
        else:
            if args.outfile is not None:
                if args.pages is not None:
                    die("PAGES specified both with and without an option flag")
                else:
                    die("--pages must be used when --even, --odd or --reverse is used")
            args.outfile = args.infile
            args.infile = args.alt_pages
    if args.pages is not None:
        cmd.append(f"-R{args.pages}")
    if args.infile is not None:
        cmd.append(args.infile)
    if args.outfile is not None:
        cmd.append(args.outfile)
    try:
        pstops(cmd)
    except SystemExit:
        die("error running pstops")


if __name__ == "__main__":
    psselect()
