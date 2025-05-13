"""PSUtils document transformer classes.

Copyright (c) Reuben Thomas 2023-2025.
Released under the GPL version 3, or (at your option) any later version.
"""

import io
import shutil
import sys
from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from typing import IO, Optional, Union
from warnings import warn

from pypdf import PdfWriter, Transformation
from pypdf.annotations import PolyLine

from .argparse import parserange
from .io import setup_input_and_output
from .readers import PdfReader, PsReader, document_reader
from .types import Offset, PageList, PageSpec, Range, Rectangle
from .warnings import die


def page_index_to_page_number(
    spec: PageSpec, maxpage: int, modulo: int, pagebase: int
) -> int:
    return (maxpage - pagebase - modulo if spec.reversed else pagebase) + spec.pageno


class DocumentTransform(ABC):
    def __init__(self) -> None:
        self.in_size: Optional[Rectangle]
        self.specs: list[list[PageSpec]]

    @abstractmethod
    def pages(self) -> int:
        pass

    @abstractmethod
    def write_header(self, maxpage: int, modulo: int) -> None:
        pass

    @abstractmethod
    def write_page_comment(self, pagelabel: str, outputpage: int) -> None:
        pass

    @abstractmethod
    def write_page(
        self,
        page_list: PageList,
        outputpage: int,
        page_specs: list[PageSpec],
        maxpage: int,
        modulo: int,
        pagebase: int,
    ) -> None:
        pass

    @abstractmethod
    def finalize(self) -> None:
        pass

    def transform_pages(
        self,
        pagerange: Optional[list[Range]],
        flipping: bool,
        reverse: bool,
        odd: bool,
        even: bool,
        modulo: int,
        verbose: bool,
    ) -> None:
        if self.in_size is None and flipping:
            die("input page size must be set when flipping the page")

        # Page spec routines for page rearrangement
        def abs_page(n: int) -> int:
            if n < 0:
                n += self.pages() + 1
                n = max(n, 1)
            return n

        def transform_pages(
            pagerange: Optional[list[Range]], odd: bool, even: bool, reverse: bool
        ) -> None:
            outputpage = 0
            # If no page range given, select all pages
            if pagerange is None:
                pagerange = parserange("1-_1")

            # Normalize end-relative pageranges
            for range_ in pagerange:
                range_.start = abs_page(range_.start)
                range_.end = abs_page(range_.end)

            # Get list of pages
            page_list = PageList(self.pages(), pagerange, reverse, odd, even)

            # Calculate highest page number output (including any blanks)
            maxpage = (
                page_list.num_pages()
                + (modulo - page_list.num_pages() % modulo) % modulo
            )

            # Rearrange pages
            self.write_header(maxpage, modulo)
            pagebase = 0
            while pagebase < maxpage:
                for page in self.specs:
                    # Construct the page label from the input page numbers
                    pagelabels = []
                    for spec in page:
                        n = page_list.real_page(
                            page_index_to_page_number(spec, maxpage, modulo, pagebase)
                        )
                        pagelabels.append(str(n + 1) if n >= 0 else "*")
                    pagelabel = ",".join(pagelabels)
                    outputpage += 1
                    self.write_page_comment(pagelabel, outputpage)
                    if verbose:
                        sys.stderr.write(f"[{pagelabel}] ")
                    self.write_page(
                        page_list, outputpage, page, maxpage, modulo, pagebase
                    )

                pagebase += modulo

            self.finalize()
            if verbose:
                print(f"\nWrote {outputpage} pages", file=sys.stderr)

        # Output the pages
        transform_pages(pagerange, odd, even, reverse)


# FIXME: Extract PsWriter.
class PsTransform(DocumentTransform):
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
        specs: list[list[PageSpec]],
        draw: float,
        in_size_guessed: bool,
    ):
        super().__init__()
        self.reader = reader
        self.outfile = outfile
        self.draw = draw
        self.specs = specs
        self.in_size_guessed = in_size_guessed

        self.use_procset = any(
            len(page) > 1 or page[0].has_transform() for page in specs
        )

        self.size = size
        if in_size is None:
            if reader.size is not None:
                in_size = reader.size
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
            except OSError:
                die("I/O error in header", 2)
            if self.size is not None:
                if self.in_size_guessed:
                    warn(f"required input paper size was guessed as {self.in_size}")
                self.write(
                    f"%%DocumentMedia: plain {int(self.size.width)} {int(self.size.height)} 0 () ()"
                )
                self.write(
                    f"%%BoundingBox: 0 0 {int(self.size.width)} {int(self.size.height)}"
                )
            pagesperspec = len(self.specs)
            self.write(f"%%Pages: {int(maxpage / modulo) * pagesperspec} 0")
        elif self.size is not None:
            warn("could not find document header, so cannot set output paper size")
        self.fcopy(self.reader.headerpos, ignorelist)
        if self.use_procset:
            self.write(f"%%BeginProcSet: PStoPS 1 15\n{self.procset}")
            self.write("%%EndProcSet")

        # Write prologue to end of setup section, skipping our procset if present
        # and we're outputting it (this allows us to upgrade our procset)
        if self.reader.procset_pos and self.use_procset:
            self.fcopy(self.reader.procset_pos.start, [])
            self.reader.infile.seek(self.reader.procset_pos.stop)
        self.fcopy(self.reader.endsetup, [])

        # Save transformation from original to current matrix
        if not self.reader.procset_pos and self.use_procset:
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
        page_specs: list[PageSpec],
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
                    assert keyword == b"Page"
                except OSError:
                    die(f"I/O error seeking page {pagenum}", 2)
            if self.use_procset:
                self.write("userdict/PStoPSsaved save put")
            if spec.has_transform():
                self.write("PStoPSmatrix setmatrix")
                if spec.off != Offset(0.0, 0.0):
                    self.write(f"{spec.off.x:f} {spec.off.y:f} translate")
                if spec.rotate != 0:
                    self.write(f"{spec.rotate % 360} rotate")
                if spec.hflip == 1:
                    assert self.in_size is not None
                    self.write(
                        f"[ -1 0 0 1 {self.in_size.width * spec.scale:g} 0 ] concat"
                    )
                if spec.vflip == 1:
                    assert self.in_size is not None
                    self.write(
                        f"[ 1 0 0 -1 0 {self.in_size.height * spec.scale:g} ] concat"
                    )
                if spec.scale != 1.0:
                    self.write(f"{spec.scale:f} dup scale")
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
                self.reader.procset_pos
                and page_number < page_list.num_pages()
                and real_page < self.pages()
            ):
                # Search for page setup
                while True:
                    try:
                        line = self.reader.infile.readline()
                    except OSError:
                        die(f"I/O error reading page setup {outputpage}", 2)
                    if line.startswith(b"PStoPSxform"):
                        break
                    try:
                        self.write(line.decode())
                    except OSError:
                        die(f"I/O error writing page setup {outputpage}", 2)
            if not self.reader.procset_pos and self.use_procset:
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
        self.reader.infile.seek(self.reader.pageptr[self.pages()])
        shutil.copyfileobj(self.reader.infile, self.outfile)
        self.outfile.flush()

    # Copy input file from current position up to new position to output file,
    # ignoring the lines starting at something ignorelist points to.
    # Updates ignorelist.
    def fcopy(self, upto: int, ignorelist: list[int]) -> None:
        here = self.reader.infile.tell()
        while len(ignorelist) > 0 and ignorelist[0] < upto:
            while len(ignorelist) > 0 and ignorelist[0] < here:
                ignorelist.pop(0)
            if len(ignorelist) > 0:
                self.fcopy(ignorelist[0], [])
            try:
                self.reader.infile.readline()
            except OSError:
                die("I/O error", 2)
            ignorelist.pop(0)
            here = self.reader.infile.tell()

        try:
            self.outfile.write(self.reader.infile.read(upto - here))
        except OSError:
            die("I/O error", 2)


class PdfTransform(DocumentTransform):
    def __init__(
        self,
        reader: PdfReader,
        outfile: IO[bytes],
        size: Optional[Rectangle],
        in_size: Optional[Rectangle],
        specs: list[list[PageSpec]],
        draw: float,
    ):
        super().__init__()
        self.outfile = outfile
        self.reader = reader
        self.writer = PdfWriter()
        self.draw = draw
        self.specs = specs

        if in_size is None:
            in_size = reader.size
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

    def write_page(
        self,
        page_list: PageList,
        outputpage: int,
        page_specs: list[PageSpec],
        maxpage: int,
        modulo: int,
        pagebase: int,
    ) -> None:
        assert self.in_size
        page_number = page_index_to_page_number(
            page_specs[0], maxpage, modulo, pagebase
        )
        real_page = page_list.real_page(page_number)
        if (
            len(page_specs) == 1
            and not page_specs[0].has_transform()
            and page_number < page_list.num_pages()
            and 0 <= real_page < len(self.reader.pages)
            and self.draw == 0
            and self.size == self.in_size
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
                        t = t.rotate(spec.rotate % 360)
                    if spec.scale != 1.0:
                        t = t.scale(spec.scale, spec.scale)
                    if spec.off != Offset(0.0, 0.0):
                        t = t.translate(spec.off.x, spec.off.y)
                    # Merge input page into the output document
                    outpdf_page.merge_transformed_page(self.reader.pages[real_page], t)
                    if self.draw > 0:  # FIXME: draw the line at the requested width
                        mediabox = self.reader.pages[real_page].mediabox
                        line = PolyLine(
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
        # PyPDF seeks, so write to a buffer first in case outfile is stdout.
        buf = io.BytesIO()
        self.writer.write(buf)
        buf.seek(0)
        self.outfile.write(buf.read())
        self.outfile.flush()


def document_transform(
    indoc: Union[PdfReader, PsReader],
    outfile: IO[bytes],
    size: Optional[Rectangle],
    in_size: Optional[Rectangle],
    specs: list[list[PageSpec]],
    draw: float,
    in_size_guessed: bool,
) -> Union[PdfTransform, PsTransform]:
    if isinstance(indoc, PsReader):
        return PsTransform(indoc, outfile, size, in_size, specs, draw, in_size_guessed)
    if isinstance(indoc, PdfReader):
        return PdfTransform(indoc, outfile, size, in_size, specs, draw)
    die("unknown document type")


@contextmanager
def file_transform(
    infile_name: str,
    outfile_name: str,
    size: Optional[Rectangle],
    in_size: Optional[Rectangle],
    specs: list[list[PageSpec]],
    draw: float,
    in_size_guessed: bool,
) -> Iterator[Union[PdfTransform, PsTransform]]:
    with setup_input_and_output(infile_name, outfile_name) as (
        infile,
        file_type,
        outfile,
    ):
        doc = document_reader(infile, file_type)
        yield document_transform(
            doc, outfile, size, in_size, specs, draw, in_size_guessed
        )
