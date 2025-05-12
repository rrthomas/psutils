"""psbook command.

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
        description="Rearrange pages in a PDF or PostScript document into signatures.",
        formatter_class=HelpFormatter,
        usage="%(prog)s [OPTION...] [INFILE [OUTFILE]]",
        add_help=False,
        epilog="""
PAGES is a comma-separated list of pages and page ranges; see pstops(1)
for more details.
""",
    )
    warnings.showwarning = simple_warning(parser.prog)

    # Command-line parser
    parser.add_argument(
        "-s",
        "--signature",
        type=int,
        default=0,
        help="""\
number of pages per signature;
0 = all pages in one signature [default];
1 = do not rearrange the pages;
otherwise, a multiple of 4""",
    )
    add_basic_arguments(parser)

    return parser


def psbook(argv: list[str] = sys.argv[1:]) -> None:
    args = get_parser().parse_intermixed_args(argv)

    if args.signature > 1 and args.signature % 4 != 0:
        die("signature must be a multiple of 4")

    # Get number of pages
    paper_context = PaperContext()
    specs, modulo, flipping = parsespecs("0", paper_context)
    with file_transform(
        args.infile, args.outfile, None, None, specs, 0, False
    ) as transform:
        input_pages = transform.pages()

        def page_index_to_real_page(signature: int, page_number: int) -> int:
            real_page = page_number - page_number % signature
            page_on_sheet = page_number % 4
            recto_verso = (page_number % signature) // 2
            if page_on_sheet in (0, 3):
                real_page += signature - 1 - recto_verso
            else:
                real_page += recto_verso
            return real_page + 1

        # Adjust for signature size
        signature = args.signature
        if signature == 0:
            maxpage = input_pages + (4 - input_pages % 4) % 4
            signature = maxpage
        else:
            maxpage = input_pages + (signature - input_pages % signature) % signature

        # Compute page list
        page_list = []
        for page in range(maxpage):
            real_page = page_index_to_real_page(signature, page)
            page_list.append(str(real_page) if real_page <= input_pages else "_")

        # Rearrange pages
        transform.transform_pages(
            parserange(",".join(page_list)),
            flipping,
            False,
            False,
            False,
            modulo,
            args.verbose,
        )


if __name__ == "__main__":
    psbook()
