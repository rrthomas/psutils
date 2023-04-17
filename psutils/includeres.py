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
from warnings import warn
from typing import List

from psutils import (
    HelpFormatter, extn, filename, setup_input_and_output, simple_warning,
)

def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description='Include resources in a PostScript document.',
        formatter_class=HelpFormatter,
        usage='%(prog)s [OPTION...] [INFILE [OUTFILE]]',
        add_help=False,
    )
    warnings.showwarning = simple_warning(parser.prog)

    parser.add_argument('--help', action='help',
                        help='show this help message and exit')
    parser.add_argument('-v', '--version', action='version',
                        version=version_banner)
    parser.add_argument('infile', metavar='INFILE', nargs='?',
                        help="`-' or no INFILE argument means standard input")
    parser.add_argument('outfile', metavar='OUTFILE', nargs='?',
                        help="`-' or no OUTFILE argument means standard output")
    return parser

def main(argv: List[str]=sys.argv[1:]) -> None: # pylint: disable=dangerous-default-value
    args = get_parser().parse_intermixed_args(argv)

    infile, outfile = setup_input_and_output(args.infile, args.outfile)

    # Include resources
    for line in infile:
        if line.startswith('%%IncludeResource:'):
            _, resource_type, *res = line.split()
            name = filename(*res)
            fullname = name
            if not os.path.exists(fullname):
                fullname += extn(resource_type)
            try:
                with open(fullname) as fh:
                    outfile.write(fh.read())
            except IOError:
                print(f'%%IncludeResource: {" ".join([resource_type, *res])}', file=outfile)
                warn(f"resource `{name}' not found")
        else:
            outfile.write(line)


if __name__ == '__main__':
    main()
