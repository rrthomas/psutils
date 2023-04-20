# PSUtils utility library
# Copyright (c) Reuben Thomas 2023.
# Released under the GPL version 3, or (at your option) any later version.

import os
import sys
import argparse
import shutil
import tempfile
import subprocess
import re
from warnings import warn
from typing import (
    Any, Callable, List, Tuple, Optional, Union, Type, NoReturn, IO, TextIO,
)

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import AnnotationBuilder

import __main__

# Help output
# Adapted from https://stackoverflow.com/questions/23936145/python-argparse-help-message-disable-metavar-for-short-options
class HelpFormatter(argparse.RawTextHelpFormatter):
    def _format_action_invocation(self, action: argparse.Action) -> str:
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
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
            parts[-1] += f' {args_string}'
        # Add space at start of format string if there is no short option
        if len(action.option_strings) > 0 and action.option_strings[0][1] == '-':
            parts[-1] = '    ' + parts[-1]
        return ', '.join(parts)

# Error messages
def simple_warning(prog:str) -> Callable[..., None]:
    def _warning( # pylint: disable=too-many-arguments
        message: Union[Warning, str],
        category: Type[Warning], # pylint: disable=unused-argument
        filename: str, # pylint: disable=unused-argument
        lineno: int, # pylint: disable=unused-argument
        file: Optional[TextIO] = sys.stderr, # pylint: disable=redefined-outer-name
        line: Optional[str] = None # pylint: disable=unused-argument
    ) -> None:
        # pylint: disable=c-extension-no-member
        print(f'\n{prog}: {message}', file=file or sys.stderr)
    return _warning

def die(msg: str, code: Optional[int] = 1) -> NoReturn:
    warn(msg)
    sys.exit(code)

# Adapted from https://github.com/python/cpython/blob/main/Lib/test/test_strtod.py
strtod_parser = re.compile(r'''    # A numeric string consists of:
    [-+]?          # an optional sign, followed by
    (?=\d|\.\d)    # a number with at least one digit
    \d*            # having a (possibly empty) integer part
    (?:\.(\d*))?   # followed by an optional fractional part
    (?:E[-+]?\d+)? # and an optional exponent
''', re.VERBOSE | re.IGNORECASE).match

def strtod(s: str) -> Tuple[float, int]:
    m = strtod_parser(s)
    if m is None:
        raise ValueError('invalid numeric string')
    return float(m[0]), m.end()

# Argument parsers
def singledimen(s: str, width: Optional[float] = None, height: Optional[float] = None) -> float:
    num, unparsed = strtod(s)
    s = s[unparsed:]

    if s.startswith('pt'):
        pass
    elif s.startswith('in'):
        num *= 72
    elif s.startswith('cm'):
        num *= 28.346456692913385211
    elif s.startswith('mm'):
        num *= 2.8346456692913385211
    elif s.startswith('w'):
        if width is None:
            die('paper size not set')
        num *= width
    elif s.startswith('h'):
        if height is None:
            die('paper size not set')
        num *= height
    elif s != '':
        die(f"bad dimension `{s}'")

    return num

# Get the size of the given paper, or the default paper if no argument given.
def paper(cmd: List[str], silent: bool = False) -> Optional[str]:
    cmd.insert(0, 'paper')
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL if silent else None, text=True)
        return out.rstrip()
    except subprocess.CalledProcessError:
        return None
    except: # pylint: disable=bare-except
        die("could not run `paper' command")

def paper_size(paper_name: Optional[str] = None) -> Tuple[Optional[float], Optional[float]]:
    if paper_name is None:
        paper_name = paper([])
    dimensions: Optional[str] = None
    if paper_name is not None:
        dimensions = paper(['--unit=pt', paper_name], True)
    if dimensions is None:
        return None, None
    m = re.search(' ([.0-9]+)x([.0-9]+) pt$', dimensions)
    assert m
    w, h = float(m[1]), float(m[2])
    return int(w + 0.5), int(h + 0.5) # round dimensions to nearest point

def parsepaper(paper: str) -> Tuple[Optional[float], Optional[float]]:
    try:
        (width, height) = paper_size(paper)
        if width is None:
            [width_text, height_text] = paper.split('x')
            if width_text and height_text:
                width, height = singledimen(width_text), singledimen(height_text)
        return width, height
    except: # pylint: disable=bare-except
        die(f"paper size '{paper}' unknown")

def parsedimen(s: str) -> float:
    return singledimen(s, None, None)

def parsedraw(s: str) -> float:
    return parsedimen(s or '1')

class PageSpec:
    reversed: bool = False
    pageno: int = 0
    rotate: int = 0
    hflip: bool = False
    vflip: bool = False
    scale: float = 1.0
    xoff: float = 0.0
    yoff: float = 0.0

    def has_transform(self) -> bool:
        return self.rotate != 0 or self.hflip or self.vflip or self.scale != 1.0 or self.xoff != 0.0 or self.yoff != 0.0

def page_index_to_page_number(ps: PageSpec, maxpage: int, modulo: int, pagebase: int) -> int:
    return (maxpage - pagebase - modulo if ps.reversed else pagebase) + ps.pageno

class Range:
    start: int
    end: int
    text: str

class PageList:
    def __init__(self, total_pages: int, pagerange: List[Range], reverse: bool, odd: bool, even: bool) -> None:
        self.pages: List[int] = []
        for r in pagerange:
            inc = -1 if r.end < r.start else 1
            currentpg = r.start
            while r.end - currentpg != -inc:
                if currentpg > total_pages:
                    die(f"page range {r.text} is invalid", 2)
                if not(odd and (not even) and currentpg % 2 == 0) and not(even and not odd and currentpg % 2 == 1):
                    self.pages.append(currentpg - 1)
                currentpg += inc
        if reverse:
            self.pages.reverse()

    # Returns -1 for an inserted blank page (page number '_')
    def real_page(self, p: int) -> int:
        try:
            return self.pages[p]
        except IndexError:
            return 0

    def num_pages(self) -> int:
        return len(self.pages)

class DocumentTransform:
    pass

class PsDocumentTransform(DocumentTransform):
    # PStoPS procset
    # Wrap showpage, erasepage and copypage in our own versions.
    # Nullify paper size operators.
    procset = '''userdict begin
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
end\n'''

    def __init__(self, infile_name: str, outfile_name: str, width: Optional[float], height: Optional[float], iwidth: Optional[float], iheight: Optional[float], specs: List[List[PageSpec]], rotate: int, scale: float, draw: float):
        self.infile, self.outfile = setup_input_and_output(infile_name, outfile_name, True)
        self.scale, self.rotate, self.draw = scale, rotate, draw
        self.global_transform = scale != 1.0 or rotate != 0
        self.specs = specs

        self.use_procset = self.global_transform or any(len(page) > 1 or page[0].has_transform() for page in specs)

        self.headerpos: int = 0
        self.pagescmt: int = 0
        self.endsetup: int = 0
        self.beginprocset: int = 0 # start of pstops procset
        self.endprocset: int = 0 # end of pstopsprocset
        self.num_pages: int = 0
        self.sizeheaders: List[int] = []
        self.pageptr: List[int] = []

        if iwidth is None and width is not None:
            iwidth, iheight = width, height
        self.width, self.height = width, height
        self.iwidth, self.iheight = iwidth, iheight

        nesting = 0
        self.infile.seek(0)
        record, next_record, buffer = 0, 0, None
        for buffer in self.infile:
            next_record += len(buffer)
            if buffer.startswith('%%'):
                keyword = self.comment_keyword(buffer)
                if keyword is not None:
                    if nesting == 0 and keyword == 'Page:':
                        self.pageptr.append(record)
                    elif self.headerpos == 0 and width is not None and \
                        keyword in ['BoundingBox:', 'HiResBoundingBox:', 'DocumentPaperSizes:', 'DocumentMedia:']:
                        # FIXME: read input paper size (from DocumentMedia comment?) if not
                        # set on command line.
                        self.sizeheaders.append(record)
                    elif self.headerpos == 0 and keyword == 'Pages:':
                        self.pagescmt = record
                    elif self.headerpos == 0 and keyword == 'EndComments':
                        self.headerpos = next_record
                    elif keyword in ['BeginDocument:', 'BeginBinary:', 'BeginFile:']:
                        nesting += 1
                    elif keyword in ['EndDocument', 'EndBinary', 'EndFile']:
                        nesting -= 1
                    elif nesting == 0 and keyword == 'EndSetup':
                        self.endsetup = record
                    elif nesting == 0 and keyword == 'BeginProlog':
                        self.headerpos = next_record
                    elif nesting == 0 and buffer == '%%BeginProcSet: PStoPS':
                        self.beginprocset = record
                    elif self.beginprocset is not None and \
                        self.endprocset is None and keyword == 'EndProcSet':
                        self.endprocset = next_record
                    elif nesting == 0 and keyword in ['Trailer', 'EOF']:
                        break
            elif self.headerpos == 0:
                self.headerpos = record
            record = next_record
        self.num_pages = len(self.pageptr)
        self.pageptr.append(record)
        if self.endsetup == 0 or self.endsetup > self.pageptr[0]:
            self.endsetup = self.pageptr[0]

    def pages(self) -> int:
        return self.num_pages

    def write_header(self, maxpage: int, modulo: int) -> None:
        # FIXME: doesn't cope properly with loaded definitions
        self.infile.seek(0)
        if self.pagescmt:
            self.fcopy(self.pagescmt, self.sizeheaders)
            try:
                _ = self.infile.readline()
            except IOError:
                die('I/O error in header', 2)
            if self.width is not None and self.height is not None:
                print(f'%%DocumentMedia: plain {int(self.width)} {int(self.height)} 0 () ()', file=self.outfile)
                print(f'%%BoundingBox: 0 0 {int(self.width)} {int(self.height)}', file=self.outfile)
            pagesperspec = len(self.specs)
            print(f'%%Pages: {int(maxpage / modulo) * pagesperspec} 0', file=self.outfile)
        self.fcopy(self.headerpos, self.sizeheaders)
        if self.use_procset:
            self.outfile.write(f'%%BeginProcSet: PStoPS 1 15\n{self.procset}')
            print("%%EndProcSet", file=self.outfile)

        # Write prologue to end of setup section, skipping our procset if present
        # and we're outputting it (this allows us to upgrade our procset)
        if self.endprocset and self.use_procset:
            self.fcopy(self.beginprocset, [])
            self.infile.seek(self.endprocset)
        self.fcopy(self.endsetup, [])

        # Save transformation from original to current matrix
        if not self.beginprocset and self.use_procset:
            print('''userdict/PStoPSxform PStoPSmatrix matrix currentmatrix
 matrix invertmatrix matrix concatmatrix
 matrix invertmatrix put''', file=self.outfile)

        # Write from end of setup to start of pages
        self.fcopy(self.pageptr[0], [])

    def write_page_comment(self, pagelabel: str, outputpage: int) -> None:
        print(f'%%Page: ({pagelabel}) {outputpage}', file=self.outfile)

    def write_page(self, page_list: PageList, outputpage: int, page: List[PageSpec], maxpage: int, modulo: int, pagebase: int) -> None:
        spec_page_number = 0
        for ps in page:
            page_number = page_index_to_page_number(ps, maxpage, modulo, pagebase)
            real_page = page_list.real_page(page_number)
            if page_number < page_list.num_pages() and 0 <= real_page < self.pages():
                # Seek the page
                p = real_page
                self.infile.seek(self.pageptr[p])
                try:
                    line = self.infile.readline()
                    assert self.comment_keyword(line) == 'Page:'
                except IOError:
                    die(f'I/O error seeking page {p}', 2)
            if self.use_procset:
                print('userdict/PStoPSsaved save put', file=self.outfile)
            if self.global_transform or ps.has_transform():
                print('PStoPSmatrix setmatrix', file=self.outfile)
                if ps.xoff is not None:
                    print(f"{ps.xoff:f} {ps.yoff:f} translate", file=self.outfile)
                if ps.rotate != 0:
                    print(f"{(ps.rotate + self.rotate) % 360} rotate", file=self.outfile)
                if ps.hflip == 1:
                    assert self.iwidth is not None
                    print(f"[ -1 0 0 1 {self.iwidth * ps.scale * self.scale:g} 0 ] concat", file=self.outfile)
                if ps.vflip == 1:
                    assert self.iheight is not None
                    print(f"[ 1 0 0 -1 0 {self.iheight * ps.scale * self.scale:g} ] concat", file=self.outfile)
                if ps.scale != 1.0:
                    print(f"{ps.scale * self.scale:f} dup scale", file=self.outfile)
                print('userdict/PStoPSmatrix matrix currentmatrix put', file=self.outfile)
                if self.iwidth is not None:
                    # pylint: disable=invalid-unary-operand-type
                    print(f'''userdict/PStoPSclip{{0 0 moveto
 {self.iwidth:f} 0 rlineto 0 {self.iheight:f} rlineto {-self.iwidth:f} 0 rlineto
 closepath}}put initclip''', file=self.outfile)
                    if self.draw > 0:
                        print(f'gsave clippath 0 setgray {self.draw} setlinewidth stroke grestore', file=self.outfile)
            if spec_page_number < len(page) - 1:
                print('/PStoPSenablepage false def', file=self.outfile)
            if self.beginprocset and page_number < page_list.num_pages() and real_page < self.pages():
                # Search for page setup
                while True:
                    try:
                        line = self.infile.readline()
                    except IOError:
                        die(f'I/O error reading page setup {outputpage}', 2)
                    if line.startswith('PStoPSxform'):
                        break
                    try:
                        print(line, file=self.outfile)
                    except IOError:
                        die(f'I/O error writing page setup {outputpage}', 2)
            if not self.beginprocset and self.use_procset:
                print('PStoPSxform concat' , file=self.outfile)
            if page_number < page_list.num_pages() and 0 <= real_page < self.pages():
                # Write the body of a page
                self.fcopy(self.pageptr[real_page + 1], [])
            else:
                print('showpage', file=self.outfile)
            if self.use_procset:
                print('PStoPSsaved restore', file=self.outfile)
            spec_page_number += 1

    def finalize(self) -> None:
        # Write trailer
        # pylint: disable=invalid-sequence-index
        self.infile.seek(self.pageptr[self.pages()])
        shutil.copyfileobj(self.infile, self.outfile)

    # Return comment keyword if `line' is a DSC comment
    def comment_keyword(self, line: str) -> Optional[str]:
        m = re.match(r'%%(\S+)', line)
        return m[1] if m else None

    # Copy input file from current position up to new position to output file,
    # ignoring the lines starting at something ignorelist points to.
    # Updates ignorelist.
    def fcopy(self, upto: int, ignorelist: List[int]) -> None:
        here = self.infile.tell()
        while len(ignorelist) > 0 and ignorelist[0] < upto:
            while len(ignorelist) > 0 and ignorelist[0] < here:
                ignorelist.pop(0)
            if len(ignorelist) > 0:
                self.fcopy(ignorelist[0], [])
            try:
                self.infile.readline()
            except IOError:
                die('I/O error', 2)
            ignorelist.pop(0)
            here = self.infile.tell()

        try:
            self.outfile.write(self.infile.read(upto - here))
        except IOError:
            die('I/O error', 2)


class PdfDocumentTransform(DocumentTransform):
    def __init__(self, infile_name: str, outfile_name: str, width: Optional[float], height: Optional[float], iwidth: Optional[float], iheight: Optional[float], specs: List[List[PageSpec]], rotate: int, scale: float, draw: float):
        self.infile, self.outfile = setup_input_and_output(infile_name, outfile_name, True, True)
        self.reader = PdfReader(self.infile)
        self.writer = PdfWriter(self.outfile)
        self.scale, self.rotate, self.draw = scale, rotate, draw
        self.global_transform = scale != 1.0 or rotate != 0
        self.specs = specs

        if iwidth is None or iheight is None:
            mediabox = self.reader.pages[0].mediabox
            iwidth, iheight = mediabox.width, mediabox.height
        if width is None or height is None:
            width, height = iwidth, iheight

        assert width is not None and height is not None
        self.width, self.height = width, height
        assert iwidth is not None and iheight is not None
        self.iwidth, self.iheight = iwidth, iheight

    def pages(self) -> int:
        return len(self.reader.pages)

    def write_header(self, maxpage: int, modulo: int) -> None:
        pass

    def write_page_comment(self, pagelabel: str, outputpage: int) -> None:
        pass

    def write_page(self, page_list: PageList, outputpage: int, page: List[PageSpec], maxpage: int, modulo: int, pagebase: int) -> None: # pylint: disable=unused-argument
        page_number = page_index_to_page_number(page[0], maxpage, modulo, pagebase)
        real_page = page_list.real_page(page_number)
        if len(page) == 1 and not self.global_transform and not page[0].has_transform() and page_number < page_list.num_pages() and 0 <= real_page < len(self.reader.pages) and self.draw == 0:
            self.writer.add_page(self.reader.pages[real_page])
        else:
            # Add a blank page of the correct size to the end of the document
            outpdf_page = self.writer.add_blank_page(self.width, self.height)
            for ps in page:
                page_number = page_index_to_page_number(ps, maxpage, modulo, pagebase)
                real_page = page_list.real_page(page_number)
                if page_number < page_list.num_pages() and 0 <= real_page < len(self.reader.pages):
                    # Calculate input page transformation
                    t = Transformation()
                    if ps.hflip:
                        t = t.transform(Transformation((-1, 0, 0, 1, self.iwidth, 0)))
                    elif ps.vflip:
                        t = t.transform(Transformation((1, 0, 0, -1, 0, self.iheight)))
                    if ps.rotate != 0:
                        t = t.rotate((ps.rotate + self.rotate) % 360)
                    if ps.scale != 1.0:
                        t = t.scale(ps.scale, ps.scale)
                    if ps.xoff is not None:
                        t = t.translate(ps.xoff, ps.yoff)
                    # Merge input page into the output document
                    outpdf_page.merge_transformed_page(self.reader.pages[real_page], t)
                    if self.draw > 0: # FIXME: draw the line at the requested width
                        mediabox = self.reader.pages[real_page].mediabox
                        line = AnnotationBuilder.polyline(
                            vertices=[
                                (mediabox.left + ps.xoff, mediabox.bottom + ps.yoff),
                                (mediabox.left + ps.xoff, mediabox.top + ps.yoff),
                                (mediabox.right + ps.xoff, mediabox.top + ps.yoff),
                                (mediabox.right + ps.xoff, mediabox.bottom + ps.yoff),
                                (mediabox.left + ps.xoff, mediabox.bottom + ps.yoff),
                            ],
                        )
                        self.writer.add_annotation(outpdf_page, line)

    def finalize(self) -> None:
        self.writer.write(self.outfile)

# Set up input and output files
def setup_input_and_output(infile_name: str, outfile_name: str, make_seekable: bool = False, binary: bool = False) -> Tuple[IO[Any], IO[Any]]:
    infile: Optional[IO[Any]] = None
    if infile_name is not None:
        try:
            infile = open(infile_name, f'r{"b" if binary else ""}')
        except IOError:
            die(f'cannot open input file {infile_name}')
    elif binary:
        infile = os.fdopen(sys.stdin.fileno(), 'rb', closefd=False)
    else:
        infile = sys.stdin
        infile.reconfigure(newline=None)
    if make_seekable:
        infile = seekable(infile)
    if infile is None:
        die('cannot make input seekable')

    if outfile_name is not None:
        try:
            outfile = open(outfile_name, f'w{"b" if binary else ""}')
        except IOError:
            die(f'cannot open output file {outfile_name}')
    elif binary:
        outfile = os.fdopen(sys.stdout.fileno(), 'wb', closefd=False)
    else:
        outfile = sys.stdout
        outfile.reconfigure(newline=None)

    return infile, outfile

# Make a file handle seekable, using a temporary file if necessary
def seekable(fp: IO[Any]) -> Optional[IO[Any]]:
    if fp.seekable():
        return fp

    try:
        ft = tempfile.TemporaryFile()
        shutil.copyfileobj(fp, ft)
        ft.seek(0)
        return ft
    except IOError:
        return None

# Resource extensions
def extn(ext: str) -> str:
    exts = {'font': '.pfa', 'file': '.ps', 'procset': '.ps',
            'pattern': '.pat', 'form': '.frm', 'encoding': '.enc'}
    return exts.get(ext, '')

# Resource filename
def filename(*components: str) -> str: # make filename for resource in 'components'
    name = ''
    for c in components: # sanitise name
        c = re.sub(r'[!()\$\#*&\\\|\`\'\"\~\{\}\[\]\<\>\?]', '', c)
        name += c
    name = os.path.basename(name) # drop directories
    if name == '':
        die(f'filename not found for resource {" ".join(components)}', 2)
    return name
