"""PSUtils I/O utilities.

Copyright (c) Reuben Thomas 2023-2025.
Released under the GPL version 3, or (at your option) any later version.
"""

import io
import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import IO

import puremagic

from .warnings import die


@contextmanager
def setup_inputs_and_output(
    infile_names: list[str | None], outfile_name: str | None
) -> Iterator[tuple[list[tuple[IO[bytes], str]], IO[bytes]]]:
    # Set up inputs
    seekable_infiles: list[tuple[IO[bytes], str]] = []
    for infile_name in infile_names:
        infile: IO[bytes]
        if infile_name is None or infile_name == "-":
            infile = os.fdopen(sys.stdin.fileno(), "rb", closefd=False)
        else:
            try:
                infile = open(infile_name, "rb")
            except OSError:
                die(f"cannot open input file {infile_name}")

        # Find MIME type of input
        data = infile.read(16)
        file_type = puremagic.from_string(data)

        # Slurp infile into a seekable BytesIO
        seekable_infile = io.BytesIO(data + infile.read())
        infile.close()

        seekable_infiles.append((seekable_infile, file_type))

    # Set up output
    if outfile_name is None or outfile_name == "-":
        outfile = os.fdopen(sys.stdout.fileno(), "wb", closefd=False)
    else:
        try:
            outfile = open(outfile_name, "wb")
        except OSError:
            die(f"cannot open output file {outfile_name}")

    # Context manager
    try:
        yield seekable_infiles, outfile
    finally:
        for infile, _ in seekable_infiles:
            infile.close()
        outfile.close()


@contextmanager
def setup_input_and_output(
    infile_name: str | None, outfile_name: str | None
) -> Iterator[tuple[IO[bytes], str, IO[bytes]]]:
    with setup_inputs_and_output([infile_name], outfile_name) as (infiles, outfile):
        yield infiles[0][0], infiles[0][1], outfile
