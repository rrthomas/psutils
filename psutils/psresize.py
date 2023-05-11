import importlib.metadata

VERSION = importlib.metadata.version('psutils')

version_banner=f'''\
%(prog)s {VERSION}
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
'''

import argparse
import sys
import warnings
from typing import List

from psutils import HelpFormatter, die, simple_warning
from psutils.psnup import psnup

def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description='Change the page size of a PDF or PostScript document.',
        formatter_class=HelpFormatter,
        usage='%(prog)s [OPTION...] [INFILE [OUTFILE]]',
        add_help=False,
        epilog='''
PAGES is a comma-separated list of pages and page ranges; see
pstops(1) for more details.
    ''',
    )
    warnings.showwarning = simple_warning(parser.prog)

    # Command-line parser
    parser.add_argument('-p', '--paper',
                        help='output paper name or dimensions (WIDTHxHEIGHT)')
    parser.add_argument('-P', '--inpaper',
                        help='input paper name or dimensions (WIDTHxHEIGHT)')
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

def psresize(argv: List[str]=sys.argv[1:]) -> None: # pylint: disable=dangerous-default-value
    args = get_parser().parse_intermixed_args(argv)

    # Resize pages
    cmd = ['-1']
    if not args.verbose:
        cmd.append('--quiet')
    if args.paper:
        cmd.extend(['--paper', args.paper])
    if args.inpaper:
        cmd.extend(['--inpaper', args.inpaper])
    if args.infile is not None:
        cmd.append(args.infile)
    if args.outfile is not None:
        cmd.append(args.outfile)
    try:
        psnup(cmd)
    except SystemExit:
        die('error running pstops')


if __name__ == '__main__':
    psresize()
