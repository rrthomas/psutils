"""psjoin command.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import os
import re
import sys
import warnings

import puremagic
from pypdf import PdfReader, PdfWriter

from psutils.argparse import HelpFormatter, add_version_argument
from psutils.warnings import die, simple_warning


def get_parser() -> argparse.ArgumentParser:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Concatenate PDF or PostScript documents.",
        formatter_class=HelpFormatter,
        usage="%(prog)s [OPTION...] FILE...",
        add_help=False,
        epilog="""
The --save and --nostrip options only apply to PostScript files.
""",
    )
    warnings.showwarning = simple_warning(parser.prog)

    # Command-line parser
    parser.add_argument(
        "-e",
        "--even",
        action="store_true",
        help="force each file to an even number of pages",
    )
    parser.add_argument(
        "-s", "--save", action="store_true", help="try to close unclosed save operators"
    )
    parser.add_argument(
        "-n",
        "--nostrip",
        action="store_true",
        help="do not strip prolog or trailer from input files",
    )
    parser.add_argument("--help", action="help", help="show this help message and exit")
    add_version_argument(parser)
    parser.add_argument(
        "file",
        metavar="FILE",
        nargs="+",
        help="`-' or no FILE argument means standard input",
    )

    return parser


# FIXME: Move the logic for merging PdfReader documents into library.
def join_pdf(args: argparse.Namespace) -> None:
    # Merge input files
    out_pdf = PdfWriter()
    for file in args.file:
        in_pdf = PdfReader(file)
        out_pdf.append(in_pdf)
        if args.even and len(in_pdf.pages) % 2 == 1:
            out_pdf.add_blank_page()

    # Write output
    out_pdf.write(sys.stdout.buffer)
    sys.stdout.buffer.flush()


# FIXME: Move the logic for merging PsReader documents into library.
def join_ps(args: argparse.Namespace) -> None:
    save = b"save %psjoin\n"
    restore = b"restore %psjoin\n"

    if args.save:
        save = b"/#psjoin-save# save def %psjoin\n"
        restore = b"#psjoin-save# restore %psjoin\n"

    prolog, prolog_inx, trailer, comments, pages = {}, None, {}, {}, {}
    if args.nostrip:
        prolog_inx = -1
        prolog[prolog_inx] = b"% psjoin: don't strip\n"
        trailer[prolog_inx] = b"% psjoin: don't strip\n"
        comments[prolog_inx] = b""
    else:
        for i, file in enumerate(args.file):
            try:
                input_ = open(file, "rb")
            except OSError as e:
                die(f"can't open file `{file}': {e}")
            with input_:
                in_comment = True
                in_prolog = True
                in_trailer = False
                comments[i] = b""
                prolog[i] = b""
                trailer[i] = b""
                pages[i] = 0
                for line in input_:
                    if line.startswith(b"%%BeginDocument"):
                        while not input_.readline().startswith(b"%%EndDocument"):
                            pass

                    if in_comment:
                        if (
                            line.startswith(b"%!PS-Adobe-")
                            or line.startswith(b"%%Title")
                            or line.startswith(b"%%Pages")
                            or line.startswith(b"%%Creator")
                        ):
                            continue
                        if line.startswith(b"%%EndComments"):
                            in_comment = False
                        comments[i] += line
                        continue
                    if in_prolog:
                        if line.startswith(b"%%Page:"):
                            in_prolog = False
                        else:
                            prolog[i] += line
                            continue

                    if line.startswith(b"%%Trailer"):
                        in_trailer = True
                    if in_trailer:
                        trailer[i] += line
                        continue

                    if line.startswith(b"%%Page:"):
                        pages[i] += 1

            if prolog[i]:
                for j in range(i):
                    if prolog[j] == prolog[i]:
                        pages[j] += pages[i]
                        break

        largest = 0
        prolog_inx = 0
        for i, file in enumerate(args.file):
            size = len(prolog[i]) * pages[i]
            if largest < size:
                largest = size
                prolog_inx = i

    files = list(map(str, map(os.path.basename, args.file)))

    sys.stdout.buffer.write(
        b"""\
%!PS-Adobe-3.0
%%Title: """
        + b" ".join([file.encode("utf-8") for file in files])
        + b"""
%%Creator: psjoin (from PSUtils)
%%Pages: (atend)\n"""
    )
    sys.stdout.buffer.write(comments[prolog_inx])

    sys.stdout.buffer.write(b"\n" + prolog[prolog_inx])
    for i in range(len(args.file)):
        if i in prolog and prolog[i]:
            prolog[i] = re.sub(b"^%%", b"% %%", prolog[i], flags=re.MULTILINE)
            trailer[i] = re.sub(b"^%%", b"% %%", trailer[i], flags=re.MULTILINE)

    total_pages = 0
    for i, file in enumerate(args.file):
        sys.stdout.buffer.write(b"% psjoin: file: " + files[i].encode("utf-8") + b"\n")
        if i not in prolog or prolog[i] != prolog[prolog_inx]:
            sys.stdout.buffer.write(
                b"% psjoin: Prolog/Trailer will be inserted in each page\n"
            )
        else:
            sys.stdout.buffer.write(b"% psjoin: common Prolog/Trailer will be used\n")

        in_document = False
        in_comment = not args.nostrip
        in_prolog = not args.nostrip
        in_trailer = False
        saved = False
        file_pages = 0

        try:
            input_ = open(file, "rb")
        except OSError as e:
            die(f"can't open file `{file[i]}': {e}")
        with input_:
            for line in input_:
                if line.startswith(b"%%BeginDocument"):
                    in_document = True
                elif line.startswith(b"%%EndDocument"):
                    in_document = False
                if in_document:
                    # s/^(%[%!])/% \1/
                    sys.stdout.buffer.write(line)
                else:
                    if in_comment:
                        if line.startswith(b"%%EndComments"):
                            in_comment = False
                    elif in_prolog:
                        if line.startswith(b"%%Page:"):
                            in_prolog = False
                        else:
                            continue
                    if not args.nostrip and line.startswith(b"%%Trailer"):
                        in_trailer = True
                    if in_trailer:
                        continue

                    if line.startswith(b"%%Page:"):
                        if saved:
                            sys.stdout.buffer.write(trailer[i])
                            sys.stdout.buffer.write(restore)
                            saved = False

                        file_pages += 1
                        total_pages += 1
                        sys.stdout.buffer.write(
                            f"\n%%Page: ({i}-{file_pages}) {total_pages}\n".encode()
                        )
                        if i not in prolog or prolog[i] != prolog[prolog_inx]:
                            sys.stdout.buffer.write(save)
                            if i in prolog:
                                sys.stdout.buffer.write(prolog[i] + b"\n")
                            saved = True
                        elif args.save:
                            sys.stdout.buffer.write(save)
                    else:
                        sys.stdout.buffer.write(re.sub(rb"^(%[%!])", rb"% \1", line))

        if args.even and file_pages % 2 != 0:
            file_pages += 1
            total_pages += 1
            sys.stdout.buffer.write(
                f"""\

%%Page: ({i}-E) {total_pages}
% psjoin: empty page inserted to force even pages
showpage\n""".encode()
            )

        if i in trailer and saved:
            sys.stdout.buffer.write(trailer[i])
        if saved or args.save:
            sys.stdout.buffer.write(restore)

    sys.stdout.buffer.write(b"\n%%Trailer\n")
    sys.stdout.buffer.write(trailer[prolog_inx])
    sys.stdout.buffer.write(f"\n%%Pages: {total_pages}\n%%EOF".encode())


def normalize_types(types: list[str]) -> list[str]:
    normalized_types = []
    for t in types:
        if t == ".eps":
            normalized_types.append(".ps")
        else:
            normalized_types.append(t)
    return normalized_types


def psjoin(argv: list[str] = sys.argv[1:]) -> None:
    args = get_parser().parse_intermixed_args(argv)

    # Check types of files
    types = list(map(puremagic.from_file, args.file))
    types = normalize_types(types)
    if not all(t == types[0] for t in types):
        die("files are not all of the same type")

    # Process the files
    if types[0] == ".pdf":
        join_pdf(args)
    elif types[0] == ".ps":
        join_ps(args)
    else:
        die(f"unknown file type `{types[0]}'")


if __name__ == "__main__":
    psjoin()
