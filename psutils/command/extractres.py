"""extractres command.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import os
import re
import sys
import warnings
from typing import IO, Optional

from psutils.argparse import HelpFormatter, add_basic_arguments
from psutils.io import setup_input_and_output
from psutils.psresources import extn, filename
from psutils.warnings import die, simple_warning


def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Extract resources from a PostScript document.",
        formatter_class=HelpFormatter,
        usage="%(prog)s [OPTION...] [INFILE [OUTFILE]]",
        add_help=False,
    )
    warnings.showwarning = simple_warning(parser.prog)

    parser.add_argument(
        "-m",
        "--merge",
        action="store_true",
        help="""merge resources of the same name into one file
(needed e.g. for fonts output in multiple blocks)""",
    )
    add_basic_arguments(parser)

    return parser


def extractres(argv: list[str] = sys.argv[1:]) -> None:
    args = get_parser().parse_intermixed_args(argv)

    with setup_input_and_output(args.infile, args.outfile) as (
        infile,
        file_type,
        outfile,
    ):
        if file_type not in (".ps", ".eps"):
            die(f"incompatible file type `{args.infile}'")

        # Resource types
        def get_type(comment: bytes) -> Optional[bytes]:
            types = {
                b"%%BeginFile:": b"file",
                b"%%BeginProcSet:": b"procset",
                b"%%BeginFont:": b"font",
            }
            return types.get(comment, None)

        # Extract resources
        resources: dict[bytes, list[bytes]] = {}  # resources included
        merge: dict[bytes, bool] = {}  # resources extracted this time
        prolog: list[bytes] = []
        body: list[bytes] = []
        output: Optional[list[bytes]] = prolog
        output_stream: Optional[IO[bytes]] = None

        saveout = None
        for line in infile:
            if re.match(b"%%Begin(Resource|Font|ProcSet):", line):
                comment, *res = line.split()  # look at resource type
                resource_type = get_type(comment) or res.pop(0)
                name = filename(*res, extn(resource_type))  # make file name
                saveout = output
                if resources.get(name) is None:
                    prolog.append(
                        b"%%IncludeResource: "
                        + resource_type
                        + b" "
                        + b" ".join(res)
                        + b"\n"
                    )
                    if not os.path.exists(name):
                        if output_stream is not None:
                            output_stream.close()
                        try:
                            output_stream = open(name, "wb")
                        except OSError:
                            die("can't write file `$name'", 2)
                        resources[name] = []
                        merge[name] = args.merge
                        output = resources[name]
                    else:  # resource already exists
                        if output_stream is not None:
                            output_stream.close()
                        output = None
                elif merge.get(name):
                    if output_stream is not None:
                        output_stream.close()
                    try:
                        output_stream = open(name, "a+b")
                    except OSError:
                        die("can't append to file `$name'", 2)
                    resources[name] = []
                    output = resources[name]
                else:  # resource already included
                    output = None
            elif re.match(b"%%End(Resource|Font|ProcSet)", line):
                if output is not None:
                    output.append(line)
                    assert output_stream is not None
                    output_stream.writelines(output)
                output = saveout
                continue
            elif re.match(b"%%End(Prolog|Setup)", line) or line.startswith(b"%%Page:"):
                output = body
            if output is not None:
                output.append(line)

        if output_stream is not None:
            output_stream.close()

        outfile.writelines(prolog)
        outfile.writelines(body)


if __name__ == "__main__":
    extractres()
