import argparse
import sys
import warnings
from typing import List, Optional, Tuple

from psutils.argparse import (
    HelpFormatter,
    PaperContext,
    add_basic_arguments,
    add_paper_arguments,
    parserange,
    parsespecs,
)
from psutils.transformers import file_transform
from psutils.types import Rectangle
from psutils.warnings import simple_warning


# Command-line parsing helper functions
def get_parser() -> Tuple[argparse.ArgumentParser, PaperContext]:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Rearrange pages of a PDF or PostScript document.",
        formatter_class=HelpFormatter,
        usage="%(prog)s [OPTION...] [INFILE [OUTFILE]]",
        add_help=False,
        epilog="""
PAGES is a comma-separated list of pages and page ranges.

SPECS is a list of page specifications [default is "0", which selects
each page in its normal order].
""",
    )
    warnings.showwarning = simple_warning(parser.prog)
    paper_context = PaperContext()

    # Command-line parser
    parser.add_argument(
        "-S",
        "--specs",
        default="0",
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
    parser.add_argument(
        "-d",
        "--draw",
        metavar="DIMENSION",
        nargs="?",
        type=paper_context.parsedraw,
        default=0,
        help="""\
draw a line of given width (relative to original
page) around each page [argument defaults to 1pt;
default is no line; width is fixed for PDF]""",
    )
    parser.add_argument("-b", "--nobind", help=argparse.SUPPRESS)
    add_basic_arguments(parser)

    return parser, paper_context


def get_parser_manpages() -> argparse.ArgumentParser:
    return get_parser()[0]


# pylint: disable=dangerous-default-value
def pstops(argv: List[str] = sys.argv[1:]) -> None:
    parser, paper_context = get_parser()
    args = parser.parse_intermixed_args(argv)
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
        args.infile, args.outfile, size, in_size, specs, args.draw
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
