"""pstops command.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import sys
import warnings
from typing import NoReturn, Optional

from psutils.argparse import (
    HelpFormatter,
    PaperContext,
    add_draw_argument,
    add_file_arguments,
    add_paper_arguments,
    add_quiet_and_help_arguments,
    add_version_argument,
    parserange,
    parsespecs,
)
from psutils.transformers import file_transform
from psutils.types import Rectangle
from psutils.warnings import simple_warning


DEFAULT_SPECS = "0"


# Command-line parsing helper functions
def get_parser() -> tuple[argparse.ArgumentParser, PaperContext]:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Rearrange pages of a PDF or PostScript document.",
        formatter_class=HelpFormatter,
        usage="%(prog)s [OPTION...] [INFILE [OUTFILE]]",
        add_help=False,
        epilog=f"""
PAGES is a comma-separated list of pages and page ranges.

SPECS is a list of page specifications [default is "{DEFAULT_SPECS}", which selects
each page in its normal order].
""",
    )
    warnings.showwarning = simple_warning(parser.prog)
    paper_context = PaperContext()

    # Command-line parser
    parser.add_argument(
        "-S",
        "--specs",
        help="page specifications (see below)",
    )
    parser.add_argument(
        "-R",
        "--pages",
        dest="pagerange",
        type=parserange,
        help="select the given page ranges",
    )
    parser.add_argument(
        "-e",
        "--even",
        action="store_true",
        help="select even-numbered output pages",
    )
    parser.add_argument(
        "-o",
        "--odd",
        action="store_true",
        help="select odd-numbered output pages",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="reverse the order of the output pages",
    )
    add_paper_arguments(parser)
    add_draw_argument(parser, paper_context)
    parser.add_argument("-b", "--nobind", help=argparse.SUPPRESS)
    add_version_argument(parser)
    add_quiet_and_help_arguments(parser)
    add_file_arguments(parser)
    # Hidden argument for backwards compatibility.
    parser.add_argument("specs_alt", nargs="?", help=argparse.SUPPRESS)

    return parser, paper_context


def get_parser_manpages() -> argparse.ArgumentParser:
    return get_parser()[0]


class SpecsException(Exception):
    pass


def spec_exception() -> NoReturn:
    raise SpecsException("invalid specs")


def pstops(argv: list[str] = sys.argv[1:]) -> None:
    parser, paper_context = get_parser()
    args = parser.parse_intermixed_args(argv)

    # Get specs if we don't have them yet
    if args.specs is None:
        if args.infile is None:
            parser.print_help()
            sys.exit(1)
        args.specs = args.infile
        try:
            parsespecs(args.specs, paper_context, err_function=spec_exception)
            args.infile = args.outfile
            args.outfile = args.specs_alt
        except SpecsException:
            args.specs = DEFAULT_SPECS

    size: Optional[Rectangle] = None
    in_size: Optional[Rectangle] = None
    if args.paper:
        size = args.paper
    elif args.width is not None and args.height is not None:
        size = Rectangle(args.width, args.height)
    if args.inpaper:
        in_size = args.inpaper
    elif args.inwidth is not None and args.inheight is not None:
        in_size = Rectangle(args.inwidth, args.inheight)
    if size:
        paper_context = PaperContext(size)
    specs, modulo, flipping = parsespecs(args.specs, paper_context)

    with file_transform(
        args.infile,
        args.outfile,
        size,
        in_size,
        specs,
        args.draw,
        False,
    ) as transform:
        transform.transform_pages(
            args.pagerange,
            flipping,
            args.reverse,
            args.odd,
            args.even,
            modulo,
            args.verbose,
        )


if __name__ == "__main__":
    pstops()
