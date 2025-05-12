"""psresize command.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import sys
import warnings

from psutils.argparse import HelpFormatter, add_basic_arguments
from psutils.command.psnup import psnup
from psutils.warnings import simple_warning


def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Change the page size of a PDF or PostScript document.",
        formatter_class=HelpFormatter,
        usage="%(prog)s [OPTION...] [INFILE [OUTFILE]]",
        add_help=False,
        epilog="""
PAGES is a comma-separated list of pages and page ranges; see
pstops(1) for more details.
    """,
    )
    warnings.showwarning = simple_warning(parser.prog)

    # Command-line parser
    parser.add_argument(
        "-p",
        "--paper",
        help="output paper name or dimensions (WIDTHxHEIGHT)",
    )
    parser.add_argument(
        "-P",
        "--inpaper",
        help="input paper name or dimensions (WIDTHxHEIGHT)",
    )
    add_basic_arguments(parser)

    # Backwards compatibility
    parser.add_argument("-w", "--width", help=argparse.SUPPRESS)
    parser.add_argument("-h", "--height", help=argparse.SUPPRESS)
    parser.add_argument("-W", "--inwidth", help=argparse.SUPPRESS)
    parser.add_argument("-H", "--inheight", help=argparse.SUPPRESS)

    return parser


def psresize(argv: list[str] = sys.argv[1:]) -> None:
    args = get_parser().parse_intermixed_args(argv)

    # Resize pages
    cmd = ["-1"]
    if not args.verbose:
        cmd.append("--quiet")
    if args.width:
        cmd.extend(["--width", args.width])
    if args.height:
        cmd.extend(["--width", args.height])
    if args.inwidth:
        cmd.extend(["--inwidth", args.inwidth])
    if args.inheight:
        cmd.extend(["--inheight", args.inheight])
    if args.paper:
        cmd.extend(["--paper", args.paper])
    if args.inpaper:
        cmd.extend(["--inpaper", args.inpaper])
    if args.infile is not None:
        cmd.append(args.infile)
    if args.outfile is not None:
        cmd.append(args.outfile)
    psnup(cmd)


if __name__ == "__main__":
    psresize()
