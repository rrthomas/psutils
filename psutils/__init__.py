"""
PSUtils utility library
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import io
import os
import sys
import argparse
import shutil
import subprocess
import re
from contextlib import contextmanager
from dataclasses import dataclass
from warnings import warn
from typing import (
    Callable,
    List,
    Tuple,
    Optional,
    Union,
    NamedTuple,
    Iterator,
    Type,
    NoReturn,
    IO,
    TextIO,
)

import puremagic  # type: ignore
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import AnnotationBuilder


# Help output
# Adapted from https://stackoverflow.com/questions/23936145/
class HelpFormatter(argparse.RawTextHelpFormatter):
    def _format_action_invocation(self, action: argparse.Action) -> str:
        if not action.option_strings:
            (metavar,) = self._metavar_formatter(action, action.dest)(1)
            return metavar
        parts: List[str] = []
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


def add_basic_arguments(parser: argparse.ArgumentParser, version_banner: str) -> None:
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
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=version_banner,
    )
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
    parser.add_argument("-w", "--width", type=parsedimen_set, help=argparse.SUPPRESS)
    parser.add_argument("-h", "--height", type=parsedimen_set, help=argparse.SUPPRESS)
    parser.add_argument("-W", "--inwidth", type=parsedimen_set, help=argparse.SUPPRESS)
    parser.add_argument("-H", "--inheight", type=parsedimen_set, help=argparse.SUPPRESS)


# Error messages
def simple_warning(prog: str) -> Callable[..., None]:
    def _warning(  # pylint: disable=too-many-arguments
        message: Union[Warning, str],
        category: Type[Warning],  # pylint: disable=unused-argument
        filename: str,  # pylint: disable=unused-argument,redefined-outer-name
        lineno: int,  # pylint: disable=unused-argument
        file: Optional[TextIO] = sys.stderr,  # pylint: disable=redefined-outer-name
        line: Optional[str] = None,  # pylint: disable=unused-argument
    ) -> None:
        # pylint: disable=c-extension-no-member
        print(f"\n{prog}: {message}", file=file or sys.stderr)

    return _warning


def die(msg: str, code: Optional[int] = 1) -> NoReturn:
    warn(msg)
    sys.exit(code)


# Adapted from https://github.com/python/cpython/blob/main/Lib/test/test_strtod.py
strtod_parser = re.compile(
    r"""    # A numeric string consists of:
    [-+]?          # an optional sign, followed by
    (?=\d|\.\d)    # a number with at least one digit
    \d*            # having a (possibly empty) integer part
    (?:\.(\d*))?   # followed by an optional fractional part
    (?:E[-+]?\d+)? # and an optional exponent
""",
    re.VERBOSE | re.IGNORECASE,
).match


def strtod(s: str) -> Tuple[float, int]:
    m = strtod_parser(s)
    if m is None:
        raise ValueError("invalid numeric string")
    return float(m[0]), m.end()


@dataclass
class Rectangle:
    width: float
    height: float


# Argument parsers
DEFAULT_PAPER_INITIALIZED: bool = False
DEFAULT_SIZE: Optional[Rectangle] = None


def singledimen(
    s: str,
    size: Optional[Rectangle] = None,
    error_message: str = "output page size not set, and could not get default paper size",
) -> float:
    global DEFAULT_SIZE, DEFAULT_PAPER_INITIALIZED  # pylint: disable=global-statement
    if not DEFAULT_PAPER_INITIALIZED:
        DEFAULT_PAPER_INITIALIZED = True
        DEFAULT_SIZE = get_paper_size()

    if size is None:
        size = DEFAULT_SIZE

    num, unparsed = strtod(s)
    s = s[unparsed:]

    if s.startswith("pt"):
        pass
    elif s.startswith("in"):
        num *= 72
    elif s.startswith("cm"):
        num *= 28.346456692913385211
    elif s.startswith("mm"):
        num *= 2.8346456692913385211
    elif s.startswith("w"):
        if size is None:
            die(error_message)
        num *= size.width
    elif s.startswith("h"):
        if size is None:
            die(error_message)
        num *= size.height
    elif s != "":
        die(f"bad dimension `{s}'")

    return num


def singledimen_set(s: str, size: Optional[Rectangle] = None) -> float:
    return singledimen(s, size, "could not get default paper size")


# Get the size of the given paper, or the default paper if no argument given.
def paper(cmd: List[str], silent: bool = False) -> Optional[str]:
    cmd.insert(0, "paper")
    try:
        out = subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL if silent else None, text=True
        )
        return out.rstrip()
    except subprocess.CalledProcessError:
        return None
    except:  # pylint: disable=bare-except
        die("could not run `paper' command")


def get_paper_size(paper_name: Optional[str] = None) -> Optional[Rectangle]:
    if paper_name is None:
        paper_name = paper(["--no-size"])
    dimensions: Optional[str] = None
    if paper_name is not None:
        dimensions = paper(["--unit=pt", paper_name], True)
    if dimensions is None:
        return None
    m = re.search(" ([.0-9]+)x([.0-9]+) pt$", dimensions)
    assert m
    w, h = float(m[1]), float(m[2])
    return Rectangle(round(w), round(h))  # round dimensions to nearest point


def parsepaper(paper_size: str) -> Optional[Rectangle]:
    try:
        size = get_paper_size(paper_size)
        if size is None:
            [width_text, height_text] = paper_size.split("x")
            if width_text and height_text:
                width = singledimen_set(width_text)
                height = singledimen_set(height_text)
            size = Rectangle(width, height)
        return size
    except:  # pylint: disable=bare-except
        die(f"paper size '{paper_size}' unknown")


def parsedimen(s: str) -> float:
    return singledimen(s, None)


def parsedimen_set(s: str) -> float:
    return singledimen_set(s, None)


def parsedraw(s: str) -> float:
    return parsedimen(s or "1")


Offset = NamedTuple("Offset", [("x", float), ("y", float)])


@dataclass
class PageSpec:
    reversed: bool = False
    pageno: int = 0
    rotate: int = 0
    hflip: bool = False
    vflip: bool = False
    scale: float = 1.0
    off: Offset = Offset(0.0, 0.0)

    def has_transform(self) -> bool:
        return (
            self.rotate != 0
            or self.hflip
            or self.vflip
            or self.scale != 1.0
            or self.off != Offset(0.0, 0.0)
        )


def page_index_to_page_number(
    spec: PageSpec, maxpage: int, modulo: int, pagebase: int
) -> int:
    return (maxpage - pagebase - modulo if spec.reversed else pagebase) + spec.pageno


@dataclass
class Range:
    start: int
    end: int
    text: str


class PageList:
    def __init__(
        self,
        total_pages: int,
        pagerange: List[Range],
        reverse: bool,
        odd: bool,
        even: bool,
    ) -> None:
        self.pages: List[int] = []
        for range_ in pagerange:
            inc = -1 if range_.end < range_.start else 1
            currentpg = range_.start
            while range_.end - currentpg != -inc:
                if currentpg > total_pages:
                    die(f"page range {range_.text} is invalid", 2)
                if not (odd and (not even) and currentpg % 2 == 0) and not (
                    even and not odd and currentpg % 2 == 1
                ):
                    self.pages.append(currentpg - 1)
                currentpg += inc
        if reverse:
            self.pages.reverse()

    # Returns -1 for an inserted blank page (page number '_')
    def real_page(self, pagenum: int) -> int:
        try:
            return self.pages[pagenum]
        except IndexError:
            return 0

    def num_pages(self) -> int:
        return len(self.pages)


class PsReader:
    def __init__(self, infile: IO[bytes]) -> None:
        self.infile = infile
        self.headerpos: int = 0
        self.pagescmt: int = 0
        self.endsetup: int = 0
        self.beginprocset: int = 0  # start of pstops procset
        self.endprocset: int = 0  # end of pstopsprocset
        self.num_pages: int = 0
        self.sizeheaders: List[int] = []
        self.pageptr: List[int] = []
        self.in_size = None

        nesting = 0
        self.infile.seek(0)
        record, next_record, buffer = 0, 0, None
        for buffer in self.infile:
            next_record += len(buffer)
            if buffer.startswith(b"%%"):
                keyword, value = self.comment(buffer)
                if keyword is not None:
                    # If input paper size is not set, try to read it
                    if (
                        self.headerpos == 0
                        and self.in_size is None
                        and keyword == b"DocumentMedia:"
                    ):
                        assert value is not None
                        words = value.split(b" ")
                        if len(words) > 2:
                            w = words[1].decode("utf-8", "ignore")
                            h = words[2].decode("utf-8", "ignore")
                            try:
                                self.in_size = Rectangle(float(w), float(h))
                            except ValueError:
                                pass
                    if nesting == 0 and keyword == b"Page:":
                        self.pageptr.append(record)
                    elif self.headerpos == 0 and keyword in [
                        b"BoundingBox:",
                        b"HiResBoundingBox:",
                        b"DocumentPaperSizes:",
                        b"DocumentMedia:",
                    ]:
                        self.sizeheaders.append(record)
                    elif self.headerpos == 0 and keyword == b"Pages:":
                        self.pagescmt = record
                    elif self.headerpos == 0 and keyword == b"EndComments":
                        self.headerpos = next_record
                    elif keyword in [
                        b"BeginDocument:",
                        b"BeginBinary:",
                        b"Begself.infile:",
                    ]:
                        nesting += 1
                    elif keyword in [b"EndDocument", b"EndBinary", b"EndFile"]:
                        nesting -= 1
                    elif nesting == 0 and keyword == b"EndSetup":
                        self.endsetup = record
                    elif nesting == 0 and keyword == b"BeginProlog":
                        self.headerpos = next_record
                    elif nesting == 0 and buffer == b"%%BeginProcSet: PStoPS":
                        self.beginprocset = record
                    elif (
                        self.beginprocset is not None
                        and self.endprocset is None
                        and keyword == b"EndProcSet"
                    ):
                        self.endprocset = next_record
                    elif nesting == 0 and keyword in [b"Trailer", b"EOF"]:
                        break
            elif self.headerpos == 0:
                self.headerpos = record
            record = next_record
        self.num_pages = len(self.pageptr)
        self.pageptr.append(record)
        if self.endsetup == 0 or self.endsetup > self.pageptr[0]:
            self.endsetup = self.pageptr[0]

    # Return comment keyword and value if `line' is a DSC comment
    def comment(self, line: bytes) -> Union[Tuple[bytes, bytes], Tuple[None, None]]:
        m = re.match(b"%%(\\S+)\\s+?(.*\\S?)\\s*$", line)
        return (m[1], m[2]) if m else (None, None)


class PsTransform:  # pylint: disable=too-many-instance-attributes
    # PStoPS procset
    # Wrap showpage, erasepage and copypage in our own versions.
    # Nullify paper size operators.
    procset = """userdict begin
[/showpage/erasepage/copypage]{dup where{pop dup load
 type/operatortype eq{ /PStoPSenablepage cvx 1 index
 load 1 array astore cvx {} bind /ifelse cvx 4 array
 astore cvx def}{pop}ifelse}{pop}ifelse}forall
 /PStoPSenablepage true def
[/letter/legal/executivepage/a4/a4small/b5/com10envelope
 /monarchenvelope/c5envelope/dlenvelope/lettersmall/note
 /folio/quarto/a5]{dup where{dup wcheck{exch{}put}
 {pop{}def}ifelse}{pop}ifelse}forall
/setpagedevice {pop}bind 1 index where{dup wcheck{3 1 roll put}
 {pop def}ifelse}{def}ifelse
/PStoPSmatrix matrix currentmatrix def
/PStoPSxform matrix def/PStoPSclip{clippath}def
/defaultmatrix{PStoPSmatrix exch PStoPSxform exch concatmatrix}bind def
/initmatrix{matrix defaultmatrix setmatrix}bind def
/initclip[{matrix currentmatrix PStoPSmatrix setmatrix
 [{currentpoint}stopped{$error/newerror false put{newpath}}
 {/newpath cvx 3 1 roll/moveto cvx 4 array astore cvx}ifelse]
 {[/newpath cvx{/moveto cvx}{/lineto cvx}
 {/curveto cvx}{/closepath cvx}pathforall]cvx exch pop}
 stopped{$error/errorname get/invalidaccess eq{cleartomark
 $error/newerror false put cvx exec}{stop}ifelse}if}bind aload pop
 /initclip dup load dup type dup/operatortype eq{pop exch pop}
 {dup/arraytype eq exch/packedarraytype eq or
  {dup xcheck{exch pop aload pop}{pop cvx}ifelse}
  {pop cvx}ifelse}ifelse
 {newpath PStoPSclip clip newpath exec setmatrix} bind aload pop]cvx def
/initgraphics{initmatrix newpath initclip 1 setlinewidth
 0 setlinecap 0 setlinejoin []0 setdash 0 setgray
 10 setmiterlimit}bind def
end"""

    def __init__(
        self,
        reader: PsReader,
        outfile: IO[bytes],
        size: Optional[Rectangle],
        in_size: Optional[Rectangle],
        specs: List[List[PageSpec]],
        rotate: int,
        scale: float,
        draw: float,
    ):
        self.reader = reader
        self.outfile = outfile
        self.scale, self.rotate, self.draw = scale, rotate, draw
        self.global_transform = scale != 1.0 or rotate != 0
        self.specs = specs

        self.use_procset = self.global_transform or any(
            len(page) > 1 or page[0].has_transform() for page in specs
        )

        self.size = size
        if in_size is None:
            if reader.in_size is not None:
                in_size = reader.in_size
            elif size is not None:
                in_size = size
        self.in_size = in_size

    def pages(self) -> int:
        return self.reader.num_pages

    def write_header(self, maxpage: int, modulo: int) -> None:
        # FIXME: doesn't cope properly with loaded definitions
        ignorelist = [] if self.size is None else self.reader.sizeheaders
        self.reader.infile.seek(0)
        if self.reader.pagescmt:
            self.fcopy(self.reader.pagescmt, ignorelist)
            try:
                _ = self.reader.infile.readline()
            except IOError:
                die("I/O error in header", 2)
            if self.size is not None:
                self.write(
                    f"%%DocumentMedia: plain {int(self.size.width)} {int(self.size.height)} 0 () ()"
                )
                self.write(
                    f"%%BoundingBox: 0 0 {int(self.size.width)} {int(self.size.height)}"
                )
            pagesperspec = len(self.specs)
            self.write(f"%%Pages: {int(maxpage / modulo) * pagesperspec} 0")
        self.fcopy(self.reader.headerpos, ignorelist)
        if self.use_procset:
            self.write(f"%%BeginProcSet: PStoPS 1 15\n{self.procset}")
            self.write("%%EndProcSet")

        # Write prologue to end of setup section, skipping our procset if present
        # and we're outputting it (this allows us to upgrade our procset)
        if self.reader.endprocset and self.use_procset:
            self.fcopy(self.reader.beginprocset, [])
            self.reader.infile.seek(self.reader.endprocset)
        self.fcopy(self.reader.endsetup, [])

        # Save transformation from original to current matrix
        if not self.reader.beginprocset and self.use_procset:
            self.write(
                """userdict/PStoPSxform PStoPSmatrix matrix currentmatrix
 matrix invertmatrix matrix concatmatrix
 matrix invertmatrix put"""
            )

        # Write from end of setup to start of pages
        self.fcopy(self.reader.pageptr[0], [])

    def write(self, text: str) -> None:
        self.outfile.write((text + "\n").encode("utf-8"))

    def write_page_comment(self, pagelabel: str, outputpage: int) -> None:
        self.write(f"%%Page: ({pagelabel}) {outputpage}")

    def write_page(
        self,
        page_list: PageList,
        outputpage: int,
        page_specs: List[PageSpec],
        maxpage: int,
        modulo: int,
        pagebase: int,
    ) -> None:
        spec_page_number = 0
        for spec in page_specs:
            page_number = page_index_to_page_number(spec, maxpage, modulo, pagebase)
            real_page = page_list.real_page(page_number)
            if page_number < page_list.num_pages() and 0 <= real_page < self.pages():
                # Seek the page
                pagenum = real_page
                self.reader.infile.seek(self.reader.pageptr[pagenum])
                try:
                    line = self.reader.infile.readline()
                    keyword, _ = self.reader.comment(line)
                    assert keyword == b"Page:"
                except IOError:
                    die(f"I/O error seeking page {pagenum}", 2)
            if self.use_procset:
                self.write("userdict/PStoPSsaved save put")
            if self.global_transform or spec.has_transform():
                self.write("PStoPSmatrix setmatrix")
                if spec.off != Offset(0.0, 0.0):
                    self.write(f"{spec.off.x:f} {spec.off.y:f} translate")
                if spec.rotate != 0:
                    self.write(f"{(spec.rotate + self.rotate) % 360} rotate")
                if spec.hflip == 1:
                    assert self.in_size is not None
                    self.write(
                        f"[ -1 0 0 1 {self.in_size.width * spec.scale * self.scale:g} 0 ] concat"
                    )
                if spec.vflip == 1:
                    assert self.in_size is not None
                    self.write(
                        f"[ 1 0 0 -1 0 {self.in_size.height * spec.scale * self.scale:g} ] concat"
                    )
                if spec.scale != 1.0:
                    self.write(f"{spec.scale * self.scale:f} dup scale")
                self.write("userdict/PStoPSmatrix matrix currentmatrix put")
                if self.in_size is not None:
                    w, h = self.in_size.width, self.in_size.height
                    self.write(
                        f"""userdict/PStoPSclip{{0 0 moveto
 {w:f} 0 rlineto 0 {h:f} rlineto {-w:f} 0 rlineto
 closepath}}put initclip"""
                    )
                    if self.draw > 0:
                        self.write(
                            f"gsave clippath 0 setgray {self.draw} setlinewidth stroke grestore"
                        )
            if spec_page_number < len(page_specs) - 1:
                self.write("/PStoPSenablepage false def")
            if (
                self.reader.beginprocset
                and page_number < page_list.num_pages()
                and real_page < self.pages()
            ):
                # Search for page setup
                while True:
                    try:
                        line = self.reader.infile.readline()
                    except IOError:
                        die(f"I/O error reading page setup {outputpage}", 2)
                    if line.startswith(b"PStoPSxform"):
                        break
                    try:
                        self.write(line.decode())
                    except IOError:
                        die(f"I/O error writing page setup {outputpage}", 2)
            if not self.reader.beginprocset and self.use_procset:
                self.write("PStoPSxform concat")
            if page_number < page_list.num_pages() and 0 <= real_page < self.pages():
                # Write the body of a page
                self.fcopy(self.reader.pageptr[real_page + 1], [])
            else:
                self.write("showpage")
            if self.use_procset:
                self.write("PStoPSsaved restore")
            spec_page_number += 1

    def finalize(self) -> None:
        # Write trailer
        # pylint: disable=invalid-sequence-index
        self.reader.infile.seek(self.reader.pageptr[self.pages()])
        shutil.copyfileobj(self.reader.infile, self.outfile)  # type: ignore
        self.outfile.flush()

    # Copy input file from current position up to new position to output file,
    # ignoring the lines starting at something ignorelist points to.
    # Updates ignorelist.
    def fcopy(self, upto: int, ignorelist: List[int]) -> None:
        here = self.reader.infile.tell()
        while len(ignorelist) > 0 and ignorelist[0] < upto:
            while len(ignorelist) > 0 and ignorelist[0] < here:
                ignorelist.pop(0)
            if len(ignorelist) > 0:
                self.fcopy(ignorelist[0], [])
            try:
                self.reader.infile.readline()
            except IOError:
                die("I/O error", 2)
            ignorelist.pop(0)
            here = self.reader.infile.tell()

        try:
            self.outfile.write(self.reader.infile.read(upto - here))
        except IOError:
            die("I/O error", 2)


class PdfTransform:  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        reader: PdfReader,
        outfile: IO[bytes],
        size: Optional[Rectangle],
        in_size: Optional[Rectangle],
        specs: List[List[PageSpec]],
        rotate: int,
        scale: float,
        draw: float,
    ):
        self.outfile = outfile
        self.reader = reader
        self.writer = PdfWriter(self.outfile)
        self.scale, self.rotate, self.draw = scale, rotate, draw
        self.global_transform = scale != 1.0 or rotate != 0
        self.specs = specs

        if in_size is None:
            mediabox = self.reader.pages[0].mediabox
            in_size = Rectangle(mediabox.width, mediabox.height)
        if size is None:
            size = in_size

        self.size = size
        self.in_size = in_size

    def pages(self) -> int:
        return len(self.reader.pages)

    def write_header(self, maxpage: int, modulo: int) -> None:
        pass

    def write_page_comment(self, pagelabel: str, outputpage: int) -> None:
        pass

    # pylint: disable=unused-argument
    def write_page(
        self,
        page_list: PageList,
        outputpage: int,
        page_specs: List[PageSpec],
        maxpage: int,
        modulo: int,
        pagebase: int,
    ) -> None:
        page_number = page_index_to_page_number(
            page_specs[0], maxpage, modulo, pagebase
        )
        real_page = page_list.real_page(page_number)
        if (  # pylint: disable=too-many-boolean-expressions
            len(page_specs) == 1
            and not self.global_transform
            and not page_specs[0].has_transform()
            and page_number < page_list.num_pages()
            and 0 <= real_page < len(self.reader.pages)
            and self.draw == 0
            and (
                self.in_size.width is None
                or (
                    self.in_size.width == self.reader.pages[real_page].mediabox.width
                    and self.in_size.height
                    == self.reader.pages[real_page].mediabox.height
                )
            )
        ):
            self.writer.add_page(self.reader.pages[real_page])
        else:
            # Add a blank page of the correct size to the end of the document
            outpdf_page = self.writer.add_blank_page(self.size.width, self.size.height)
            for spec in page_specs:
                page_number = page_index_to_page_number(spec, maxpage, modulo, pagebase)
                real_page = page_list.real_page(page_number)
                if page_number < page_list.num_pages() and 0 <= real_page < len(
                    self.reader.pages
                ):
                    # Calculate input page transformation
                    t = Transformation()
                    if spec.hflip:
                        t = t.transform(
                            Transformation((-1, 0, 0, 1, self.in_size.width, 0))
                        )
                    elif spec.vflip:
                        t = t.transform(
                            Transformation((1, 0, 0, -1, 0, self.in_size.height))
                        )
                    if spec.rotate != 0:
                        t = t.rotate((spec.rotate + self.rotate) % 360)
                    if spec.scale != 1.0:
                        t = t.scale(spec.scale, spec.scale)
                    if spec.off != Offset(0.0, 0.0):
                        t = t.translate(spec.off.x, spec.off.y)
                    # Merge input page into the output document
                    outpdf_page.merge_transformed_page(self.reader.pages[real_page], t)
                    if self.draw > 0:  # FIXME: draw the line at the requested width
                        mediabox = self.reader.pages[real_page].mediabox
                        line = AnnotationBuilder.polyline(
                            vertices=[
                                (
                                    mediabox.left + spec.off.x,
                                    mediabox.bottom + spec.off.y,
                                ),
                                (mediabox.left + spec.off.x, mediabox.top + spec.off.y),
                                (
                                    mediabox.right + spec.off.x,
                                    mediabox.top + spec.off.y,
                                ),
                                (
                                    mediabox.right + spec.off.x,
                                    mediabox.bottom + spec.off.y,
                                ),
                                (
                                    mediabox.left + spec.off.x,
                                    mediabox.bottom + spec.off.y,
                                ),
                            ],
                        )
                        self.writer.add_annotation(outpdf_page, line)

    def finalize(self) -> None:
        self.writer.write(self.outfile)
        self.outfile.flush()


@contextmanager
def document_transform(
    infile_name: str,
    outfile_name: str,
    size: Optional[Rectangle],
    in_size: Optional[Rectangle],
    specs: List[List[PageSpec]],
    rotate: int,
    scale: float,
    draw: float,
) -> Iterator[Union[PdfTransform, PsTransform]]:
    with setup_input_and_output(infile_name, outfile_name) as (
        infile,
        file_type,
        outfile,
    ):
        if file_type in (".ps", ".eps"):
            yield PsTransform(
                PsReader(infile),
                outfile,
                size,
                in_size,
                specs,
                rotate,
                scale,
                draw,
            )
        elif file_type == ".pdf":
            yield PdfTransform(
                PdfReader(infile),
                outfile,
                size,
                in_size,
                specs,
                rotate,
                scale,
                draw,
            )
        else:
            die(f"incompatible file type `{infile_name}'")


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


# Resource extensions
def extn(ext: bytes) -> bytes:
    exts = {
        b"font": b".pfa",
        b"file": b".ps",
        b"procset": b".ps",
        b"pattern": b".pat",
        b"form": b".frm",
        b"encoding": b".enc",
    }
    return exts.get(ext, b"")


# Resource filename
def filename(*components: bytes) -> bytes:  # make filename for resource in 'components'
    name = b""
    for component in components:  # sanitise name
        c_str = component.decode()
        c_str = re.sub(r"[!()\$\#*&\\\|\`\'\"\~\{\}\[\]\<\>\?]", "", c_str)
        name += c_str.encode()
    name = os.path.basename(name)  # drop directories
    if name == b"":
        die(f'filename not found for resource {b" ".join(components).decode()}', 2)
    return name
