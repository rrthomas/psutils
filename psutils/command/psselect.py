"""psselect command.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import sys
import warnings

from psutils.argparse import (
    HelpFormatter,
    PaperContext,
    add_basic_arguments,
    parserange,
    parsespecs,
)
from psutils.transformers import file_transform
from psutils.warnings import die, simple_warning


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
    add_basic_arguments(parser)

    return parser


def psselect(argv: list[str] = sys.argv[1:]) -> None:
    args = get_parser().parse_intermixed_args(argv)

    # Get page range argument if supplied as a non-option
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

    # Rearrange pages
    pagerange = parserange(args.pages) if args.pages is not None else None
    paper_context = PaperContext()
    specs, modulo, flipping = parsespecs("0", paper_context)
    with file_transform(
        args.infile, args.outfile, None, None, specs, 0, False
    ) as transform:
        transform.transform_pages(
            pagerange, flipping, args.reverse, args.odd, args.even, modulo, args.verbose
        )


if __name__ == "__main__":
    psselect()
