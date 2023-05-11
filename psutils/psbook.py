import importlib.metadata
import argparse
import sys
import warnings
from typing import List

from psutils import (
    HelpFormatter, die, simple_warning, documentTransform,
)
from psutils.pstops import pstops

VERSION = importlib.metadata.version('psutils')

version_banner='''\
%(prog)s {VERSION}
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
'''

def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description='Rearrange pages in a PDF or PostScript document into signatures.',
        formatter_class=HelpFormatter,
        usage='%(prog)s [OPTION...] [INFILE [OUTFILE]]',
        add_help=False,
        epilog='''
PAGES is a comma-separated list of pages and page ranges; see pstops(1)
for more details.
''',
    )
    warnings.showwarning = simple_warning(parser.prog)

    # Command-line parser
    parser.add_argument('-s', '--signature', type=int, default=0, help='''\
number of pages per signature;
0 = all pages in one signature [default];
1 = do not rearrange the pages;
otherwise, a multiple of 4''')
    parser.add_argument('-q', '--quiet', action='store_false', dest='verbose',
                        help="don't show page numbers being output")
    parser.add_argument('--help', action='help',
                        help='show this help message and exit')
    parser.add_argument('-v', '--version', action='version',
                        version=version_banner)
    parser.add_argument('infile', metavar='INFILE', nargs='?',
                        help="`-' or no INFILE argument means standard input")
    parser.add_argument('outfile', metavar='OUTFILE', nargs='?',
                        help="`-' or no OUTFILE argument means standard output")
    return parser

def psbook(argv: List[str]=sys.argv[1:]) -> None: # pylint: disable=dangerous-default-value
    args = get_parser().parse_intermixed_args(argv)

    if args.signature > 1 and args.signature % 4 != 0:
        die('signature must be a multiple of 4')

    # Get number of pages
    with documentTransform(args.infile, args.outfile, None, None, None, None, [], False, 1.0, 0) as doc:
        input_pages = doc.pages()

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
            page_list.append(str(real_page) if real_page <= input_pages else '_')

        # Rearrange pages
        cmd = []
        if not args.verbose:
            cmd.append('--quiet')
        cmd.append(f'--pages={",".join(page_list)}')
        if args.infile is not None:
            cmd.append(args.infile)
        if args.outfile is not None:
            cmd.append(args.outfile)
        try:
            pstops(cmd)
        except SystemExit:
            die('error running pstops')


if __name__ == '__main__':
    psbook()
