"""psnup command.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import re
import sys
import warnings
from collections.abc import Sequence
from copy import copy
from typing import Any, Optional, Union

from psutils.argparse import (
    HelpFormatter,
    PaperContext,
    add_basic_arguments,
    add_draw_argument,
    add_paper_arguments,
    parsespecs,
)
from psutils.io import setup_input_and_output
from psutils.libpaper import get_paper_size
from psutils.readers import document_reader
from psutils.transformers import document_transform
from psutils.types import Rectangle
from psutils.warnings import die, simple_warning


def parsenup(s: str) -> int:
    if not re.match(r"-\d+", s):
        die(f'value "{s}" invalid for -NUMBER (number expected)')
    n = -int(s)
    if n == 0:
        die("number of pages per sheet must be greater than 0")
    return n


class ToggleAction(argparse.Action):
    def __init__(
        self,
        option_strings: list[str],
        dest: str,
        nargs: Optional[str] = None,
        default: bool = False,
        **kwargs: Any,
    ) -> None:
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, nargs=0, default=default, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Union[str, Sequence[Any], None],
        option_string: Optional[str] = None,
    ) -> None:
        setattr(namespace, self.dest, not getattr(namespace, self.dest))


def get_parser() -> tuple[argparse.ArgumentParser, PaperContext]:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Put multiple pages of a PostScript document on to one page.",
        formatter_class=HelpFormatter,
        usage="%(prog)s [OPTION...] -NUMBER [INFILE [OUTFILE]]",
        add_help=False,
        epilog="""
psnup aborts with an error if it cannot arrange the input pages so as to
waste less than the given tolerance.

The output page size defaults to the input page size; if none is specified
in the document or on the command line, the default given by the `paper'
command is used.

The input page size defaults to the output page size.

In row-major order (the default), adjacent pages are placed in rows
across the paper; in column-major order, they are placed in columns down
the page.
""",
    )
    warnings.showwarning = simple_warning(parser.prog)
    paper_context = PaperContext()

    # Command-line parser
    add_paper_arguments(parser)
    parser.add_argument(
        "-m",
        "--margin",
        metavar="DIMENSION",
        type=paper_context.dimension,
        default=0,
        help="""\
width of margin around each output page
[default 0pt]; useful for thumbnail sheets,
as the original page margins will be shrunk""",
    )
    parser.add_argument(
        "-b",
        "--border",
        metavar="DIMENSION",
        type=paper_context.dimension,
        default=0,
        help="width of border around each input page",
    )
    add_draw_argument(parser, paper_context)
    parser.add_argument(
        "-l",
        "--rotatedleft",
        action=ToggleAction,
        help="input pages are rotated left 90 degrees",
    )
    parser.add_argument(
        "-r",
        "--rotatedright",
        action=ToggleAction,
        help="input pages are rotated right 90 degrees",
    )
    parser.add_argument(
        "-f", "--flip", action=ToggleAction, help="swap output pages' width and height"
    )
    parser.add_argument(
        "-c",
        "--transpose",
        action=ToggleAction,
        help="swap columns and rows (column-major order)",
    )
    parser.add_argument(
        "-t",
        "--tolerance",
        metavar="NUMBER",
        type=int,
        default=100_000,
        help="maximum wasted area in square pt [default: %(default)s]",
    )
    parser.add_argument(
        "nup",
        metavar="-NUMBER",
        type=parsenup,
        help="number of pages to impose on each output page",
    )
    add_basic_arguments(parser)

    return parser, paper_context


def get_parser_manpages() -> argparse.ArgumentParser:
    return get_parser()[0]


# FIXME: Move calculation logic into DocumentTransform class.
def psnup(argv: list[str] = sys.argv[1:]) -> None:
    parser, paper_context = get_parser()
    args = parser.parse_intermixed_args(argv)
    size: Optional[Rectangle] = None
    in_size: Optional[Rectangle] = None

    with setup_input_and_output(
        args.infile,
        args.outfile,
    ) as (infile, file_type, outfile):
        doc = document_reader(infile, file_type)
        if args.paper:
            size = args.paper
        elif args.width is not None and args.height is not None:
            size = Rectangle(args.width, args.height)
        if args.inpaper:
            in_size = args.inpaper
        elif args.inwidth is not None and args.inheight is not None:
            in_size = Rectangle(args.inwidth, args.inheight)
        elif doc.size is not None and not doc.size_guessed:
            in_size = Rectangle(doc.size.width, doc.size.height)

        # Process command-line arguments
        rowmajor, leftright, topbottom = True, True, True
        if args.transpose:
            rowmajor = False
        if args.rotatedleft:
            rowmajor = not rowmajor
            topbottom = not topbottom
        if args.rotatedright:
            rowmajor = not rowmajor
            leftright = not leftright

        if size is None and ((args.width is None) ^ (args.height is None)):
            die("output page width and height must both be set, or neither")
        if in_size is None and ((args.inwidth is None) ^ (args.inheight is None)):
            die("input page width and height must both be set, or neither")

        # If input page size is undefined, use guess or output value if available
        in_size_guessed = False
        if in_size is None:
            in_size = doc.size if doc.size is not None else size
            in_size_guessed = True

        # If output page size is undefined, set from input value if available
        if size is None and in_size is not None:
            size = copy(in_size)

        # Ensure input and output page sizes are set, using `paper` if necessary
        if size is None:
            paper_size = get_paper_size()
            if paper_size is not None:
                size = paper_size
                in_size = paper_size
        if size is None:
            die("output page size not set, and could not get default paper size")
        assert(in_size)

        # Take account of flip
        if args.flip:
            size = Rectangle(size.height, size.width)

        # Find next larger exact divisor > n of m, or 0 if none; return divisor
        # and dividend.
        # There is probably a much more efficient method of doing this, but the
        # numbers involved are small.
        def nextdiv(n: int, m: int) -> tuple[int, int]:
            while n < m:
                n += 1
                if m % n == 0:
                    return n, m // n
            return 0, 0

        # Calculate paper dimensions, subtracting paper margin from height & width
        ppwid, pphgt = size.width - args.margin * 2, size.height - args.margin * 2
        if ppwid <= 0 or pphgt <= 0:
            die("margin is too large")
        if args.border > min(ppwid, pphgt):
            die("border is too large")

        # Finding the best layout is an optimisation problem. We try all of the
        # combinations of width*height in both normal and rotated form, and
        # minimise the wasted space.
        best = args.tolerance
        horiz = 0.0
        vert = 0.0
        rotate = False

        def reduce_waste(
            hor: float, ver: float, iwid: float, ihgt: float, rot: bool
        ) -> None:
            nonlocal best, horiz, vert, rotate
            scl = min(pphgt / (ihgt * ver), ppwid / (iwid * hor))
            waste = (ppwid - scl * iwid * hor) ** 2 + (pphgt - scl * ihgt * ver) ** 2
            if waste < best:
                best, horiz, vert, rotate = waste, hor, ver, rot

        hor, ver = 1, args.nup
        while hor != 0:
            reduce_waste(
                hor, ver, in_size.width, in_size.height, False
            )  # normal orientation
            reduce_waste(
                ver, hor, in_size.height, in_size.width, True
            )  # rotated orientation
            hor, ver = nextdiv(hor, args.nup)

        # Fail if nothing better than tolerance was found
        if best == args.tolerance:
            die(f"can't find acceptable layout for {args.nup}-up")

        # Take account of rotation
        orig_in_size = copy(in_size)
        if rotate:
            topbottom, leftright, rowmajor, in_size.width, in_size.height = (
                not leftright,
                topbottom,
                not rowmajor,
                in_size.height,
                in_size.width,
            )

        # Calculate page scale, allowing for internal borders
        scale = min(
            (pphgt - 2 * args.border * vert) / (in_size.height * vert),
            (ppwid - 2 * args.border * horiz) / (in_size.width * horiz),
        )

        # Page centring shifts
        hshift, vshift = (ppwid / horiz - in_size.width * scale) / 2, (
            pphgt / vert - in_size.height * scale
        ) / 2

        # Construct specification list
        spec_list = []
        for page in range(args.nup):
            across, up = (
                (page % horiz, page // horiz)
                if rowmajor
                else (page // vert, page % vert)
            )
            if not leftright:
                across = horiz - 1 - across
            if topbottom:
                up = vert - 1 - up
            if rotate:
                xoff = args.margin + (across + 1) * ppwid / horiz - hshift
            else:
                xoff = args.margin + across * ppwid / horiz + hshift
            yoff = args.margin + up * pphgt / vert + vshift
            spec_list.append(
                f'{page}{"L" if rotate else ""}@{scale:f}({xoff:f},{yoff:f})'
            )

        # Rearrange pages
        specs, modulo, flipped = parsespecs(
            f'{args.nup}:{"+".join(spec_list)}', paper_context
        )
        transform = document_transform(
            doc, outfile, size, orig_in_size, specs, args.draw, in_size_guessed
        )
        transform.transform_pages(
            None, flipped, False, False, False, modulo, args.verbose
        )


if __name__ == "__main__":
    psnup()
