"""PSUtils argparse type parsers.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import importlib.metadata
import re
from typing import Callable, NoReturn, Optional

from .libpaper import get_paper_size
from .types import Offset, PageSpec, Range, Rectangle
from .warnings import die


# Argument parsers
def parserange(ranges_text: str) -> list[Range]:
    ranges = []
    for range_text in ranges_text.split(","):
        range_ = Range(0, 0, range_text)
        if range_.text != "_":
            m = re.match(r"(_?\d+)?(?:(-)(_?\d+))?$", range_.text)
            if not m:
                die(f"`{range_.text}' is not a page range")
            start = m[1] or "1"
            end = (m[3] or "-1") if m[2] else m[1]
            start = re.sub("^_", "-", start)
            end = re.sub("^_", "-", end)
            range_.start, range_.end = int(start), int(end)
        ranges.append(range_)
    return ranges


def parsepaper(paper_size: str) -> Optional[Rectangle]:
    try:
        size = get_paper_size(paper_size)
        if size is None:
            [width_text, height_text] = paper_size.split("x")
            if width_text and height_text:
                width = dimension(width_text)
                height = dimension(height_text)
                size = Rectangle(width, height)
        return size
    except Exception:
        die(f"paper size '{paper_size}' unknown")


units = {
    "": 1,
    "pt": 1,
    "in": 72,
    "cm": 28.346456692913385211,
    "mm": 2.8346456692913385211,
}


def dimension(s: str) -> float:
    m = re.match(r"(.+?)(|pt|in|cm|mm)$", s)
    if not m:
        raise ValueError(f"bad dimension `{s}'")

    return float(m[1]) * units[m[2]]


class PaperContext:
    def __init__(self, size: Optional[Rectangle] = None) -> None:
        if size is None:
            # Run get_paper_size at run-time, so we have already set up the
            # warning handler.
            size = get_paper_size()
        self.default_paper = size

    def dimension(
        self,
        s: str,
    ) -> float:
        try:
            num = dimension(s)
        except ValueError:
            m = re.match(r"(.+?)(w|h)$", s)
            if not m:
                die(f"bad dimension `{s}'")
            num, dim = float(m[1]), m[2]

            size = self.default_paper
            if size is None:
                die("output page size not set, and could not get default paper size")
            if dim == "w":
                num *= size.width
            elif dim == "h":
                num *= size.height

        return num


def specerror() -> NoReturn:
    die(
        """bad page specification:

  PAGESPECS = [MODULO:]SPECS
  SPECS     = SPEC[+SPECS|,SPECS]
  SPEC      = [-]PAGENO[TRANSFORM...][@SCALE][(XOFF,YOFF)]
  TRANSFORM = L|R|U|H|V
              MODULO > 0; 0 <= PAGENO < MODULO"""
    )


def parsespecs(
    s: str,
    paper_context: PaperContext,
    err_function: Callable[[], NoReturn] = specerror,
) -> tuple[list[list[PageSpec]], int, bool]:
    flipping = False
    m = re.match(r"(?:([^:]+):)?(.*)", s)
    if not m:
        err_function()
    modulo, specs_text = int(m[1] or "1"), m[2]
    # Split on commas but not inside parentheses.
    pages_text = re.split(r",(?![^()]*\))", specs_text)
    pages = []
    angle = {"l": 90, "r": -90, "u": 180}
    for page in pages_text:
        specs = []
        specs_text = page.split("+")
        for spec_text in specs_text:
            m = re.match(
                r"(-)?(\d+)([LRUHV]+)?(?:@([^()]+))?(?:\((-?[\d.a-z]+,-?[\d.a-z]+)\))?$",
                spec_text,
                re.IGNORECASE | re.ASCII,
            )
            if not m:
                err_function()
            spec = PageSpec()
            if m[1] is not None:
                spec.reversed = True
            if m[2] is not None:
                spec.pageno = int(m[2])
            if m[4] is not None:
                spec.scale = float(m[4])
            if m[5] is not None:
                [xoff_str, yoff_str] = m[5].split(",")
                spec.off = Offset(
                    paper_context.dimension(xoff_str),
                    paper_context.dimension(yoff_str),
                )
            if spec.pageno >= modulo:
                err_function()
            if m[3] is not None:
                for mod in m[3]:
                    if re.match(r"[LRU]", mod, re.IGNORECASE):
                        spec.rotate += angle[mod.lower()]
                    elif re.match(r"H", mod, re.IGNORECASE):
                        spec.hflip = not spec.hflip
                    elif re.match(r"V", mod, re.IGNORECASE):
                        spec.vflip = not spec.vflip
            # Normalize rotation and flips
            if spec.hflip and spec.vflip:
                spec.hflip, spec.vflip = False, False
                spec.rotate += 180
            spec.rotate %= 360
            if spec.hflip or spec.vflip:
                flipping = True
            specs.append(spec)
        pages.append(specs)
    return pages, modulo, flipping


# Help output
# Adapted from https://stackoverflow.com/questions/23936145/
class HelpFormatter(argparse.RawTextHelpFormatter):
    def _format_action_invocation(self, action: argparse.Action) -> str:
        if not action.option_strings:
            (metavar,) = self._metavar_formatter(action, action.dest)(1)
            return metavar
        parts: list[str] = []
        if action.nargs == 0:
            # Option takes no argument, output: -s, --long
            parts.extend(action.option_strings)
        else:
            # Option takes an argument, output: -s, --long ARGUMENT
            default = action.dest.upper()
            args_string = self._format_args(action, default)
            for option_string in action.option_strings:
                parts.append(option_string)
            parts[-1] += f" {args_string}"
        # Add space at start of format string if there is no short option
        if len(action.option_strings) > 0 and action.option_strings[0][1] == "-":
            parts[-1] = "    " + parts[-1]
        return ", ".join(parts)


VERSION = importlib.metadata.version("psutils")

VERSION_BANNER = f"""\
%(prog)s {VERSION}
Copyright (c) Reuben Thomas 2023-2025.
Licence GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


def add_version_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=VERSION_BANNER,
    )


def add_quiet_and_help_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="don't show progress",
    )
    parser.add_argument(
        "--help",
        action="help",
        help="show this help message and exit",
    )


def add_basic_arguments(parser: argparse.ArgumentParser) -> None:
    add_version_argument(parser)
    add_quiet_and_help_arguments(parser)
    add_file_arguments(parser)


def add_file_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "infile",
        metavar="INFILE",
        nargs="?",
        help="`-' or no INFILE argument means standard input",
    )
    parser.add_argument(
        "outfile",
        metavar="OUTFILE",
        nargs="?",
        help="`-' or no OUTFILE argument means standard output",
    )


def add_paper_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-p",
        "--paper",
        type=parsepaper,
        help="output paper name or dimensions (WIDTHxHEIGHT)",
    )
    parser.add_argument(
        "-P",
        "--inpaper",
        type=parsepaper,
        help="input paper name or dimensions (WIDTHxHEIGHT)",
    )

    # Backwards compatibility
    parser.add_argument("-w", "--width", type=dimension, help=argparse.SUPPRESS)
    parser.add_argument("-h", "--height", type=dimension, help=argparse.SUPPRESS)
    parser.add_argument("-W", "--inwidth", type=dimension, help=argparse.SUPPRESS)
    parser.add_argument("-H", "--inheight", type=dimension, help=argparse.SUPPRESS)


def add_draw_argument(
    parser: argparse.ArgumentParser, paper_context: PaperContext
) -> None:
    parser.add_argument(
        "-d",
        "--draw",
        metavar="DIMENSION",
        nargs="?",
        type=paper_context.dimension,
        default=0,
        const=1,
        help="""\
draw a line of given width (relative to original
page) around each page [argument defaults to 1pt;
default is no line; width is fixed for PDF]""",
    )
