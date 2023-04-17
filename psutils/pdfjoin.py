import pkg_resources

VERSION = pkg_resources.require('psutils')[0].version
version_banner=f'''\
%(prog)s {VERSION}
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
'''

import argparse
import os
import sys
import warnings
from typing import List

from pypdf import PdfReader, PdfWriter

from psutils import HelpFormatter, simple_warning

def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description='Concatenate PDF documents.',
        formatter_class=HelpFormatter,
        usage='%(prog)s [OPTION...] FILE...',
        add_help=False,
    )
    warnings.showwarning = simple_warning(parser.prog)

    # Command-line parser
    parser.add_argument('-e', '--even', action='store_true',
                        help='force each file to an even number of pages')
    parser.add_argument('--help', action='help',
                        help='show this help message and exit')
    parser.add_argument('-v', '--version', action='version',
                        version=version_banner)
    parser.add_argument('file', metavar='FILE', nargs='+',
                        help="`-' or no FILE argument means standard input")
    return parser

def main(argv: List[str]=sys.argv[1:]) -> None: # pylint: disable=dangerous-default-value
    args = get_parser().parse_intermixed_args(argv)

    # Merge input files
    out_pdf = PdfWriter()
    for file in args.file:
        in_pdf = PdfReader(file)
        out_pdf.append(in_pdf)
        if args.even and len(in_pdf.pages) % 2 == 1:
            out_pdf.add_blank_page()

    # Write output
    outfile = os.fdopen(sys.stdout.fileno(), 'wb', closefd=False)
    out_pdf.write(outfile)


if __name__ == '__main__':
    main()
