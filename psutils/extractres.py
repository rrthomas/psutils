import importlib.metadata
import argparse
import os
import re
import sys
import warnings
from typing import Dict, List, Optional, IO

from psutils import (
    HelpFormatter,
    add_basic_arguments,
    die,
    extn,
    filename,
    setup_input_and_output,
    simple_warning,
)

VERSION = importlib.metadata.version("psutils")

version_banner = f"""\
%(prog)s {VERSION}
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""


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
    add_basic_arguments(parser, version_banner)

    return parser


# pylint: disable=dangerous-default-value
def extractres(
    argv: List[str] = sys.argv[1:],
) -> None:
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
        resources: Dict[bytes, List[bytes]] = {}  # resources included
        merge: Dict[bytes, bool] = {}  # resources extracted this time
        prolog: List[bytes] = []
        body: List[bytes] = []
        output: Optional[List[bytes]] = prolog
        fh: Optional[IO[bytes]] = None

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
                        try:
                            fh = open(name, "wb")
                        except IOError:
                            die("can't write file `$name'", 2)
                        resources[name] = []
                        merge[name] = args.merge
                        output = resources[name]
                    else:  # resource already exists
                        if fh is not None:
                            fh.close()
                        output = None
                elif merge.get(name):
                    try:
                        fh = open(name, "a+b")  # pylint: disable=consider-using-with
                    except IOError:
                        die("can't append to file `$name'", 2)
                    resources[name] = []
                    output = resources[name]
                else:  # resource already included
                    output = None
            elif re.match(b"%%End(Resource|Font|ProcSet)", line):
                if output is not None:
                    output.append(line)
                    assert fh is not None
                    fh.writelines(output)
                output = saveout
                continue
            elif re.match(b"%%End(Prolog|Setup)", line) or line.startswith(b"%%Page:"):
                output = body
            if output is not None:
                output.append(line)

        outfile.writelines(prolog)
        outfile.writelines(body)


if __name__ == "__main__":
    extractres()
