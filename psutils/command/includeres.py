"""includeres command.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import os
import sys
import warnings
from warnings import warn

from psutils.argparse import HelpFormatter, add_basic_arguments
from psutils.io import setup_input_and_output
from psutils.psresources import extn, filename
from psutils.warnings import die, simple_warning


def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Include resources in a PostScript document.",
        formatter_class=HelpFormatter,
        usage="%(prog)s [OPTION...] [INFILE [OUTFILE]]",
        add_help=False,
    )
    warnings.showwarning = simple_warning(parser.prog)
    add_basic_arguments(parser)

    return parser


def includeres(argv: list[str] = sys.argv[1:]) -> None:
    args = get_parser().parse_intermixed_args(argv)

    with setup_input_and_output(args.infile, args.outfile) as (
        infile,
        file_type,
        outfile,
    ):
        if file_type not in (".ps", ".eps"):
            die(f"incompatible file type `{args.infile}'")

        # Include resources
        for line in infile:
            if line.startswith(b"%%IncludeResource:"):
                _, resource_type, *res = line.split()
                name = filename(*res)
                fullname = name
                if not os.path.exists(fullname):
                    fullname += extn(resource_type)
                try:
                    with open(fullname, "rb") as f:
                        outfile.write(f.read())
                except OSError:
                    outfile.write(
                        f'%%IncludeResource: {b" ".join([resource_type, *res]).decode()}\n'.encode()
                    )
                    warn(f"resource `{name.decode()}' not found")
            else:
                outfile.write(line)


if __name__ == "__main__":
    includeres()
