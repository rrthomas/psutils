"""
PSUtils I/O utilities.
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import io
import os
import sys
from contextlib import contextmanager
from typing import Tuple, Optional, Iterator, IO

import puremagic

from .warnings import die


@contextmanager
def setup_input_and_output(
    infile_name: Optional[str], outfile_name: Optional[str]
) -> Iterator[Tuple[IO[bytes], str, IO[bytes]]]:
    # Set up input
    infile: Optional[IO[bytes]] = None
    if infile_name is not None:
        try:
            infile = open(infile_name, "rb")
        except IOError:
            die(f"cannot open input file {infile_name}")
    else:
        infile = os.fdopen(sys.stdin.fileno(), "rb", closefd=False)

    # Find MIME type of input
    data = infile.read(16)
    file_type = puremagic.from_string(data)

    # Slurp infile into a seekable BytesIO
    infile = io.BytesIO(data + infile.read())

    # Set up output
    if outfile_name is not None:
        try:
            outfile = open(outfile_name, "wb")
        except IOError:
            die(f"cannot open output file {outfile_name}")
    else:
        outfile = os.fdopen(sys.stdout.fileno(), "wb", closefd=False)

    # Context manager
    try:
        yield infile, file_type, outfile
    finally:
        infile.close()
        outfile.close()
