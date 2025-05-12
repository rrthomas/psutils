"""PSUtils document reader classes.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import re
from pathlib import Path
from typing import IO, Union

from pypdf import PdfReader as PdfReaderBase
from pypdf._utils import StrByteType

from .types import Rectangle
from .warnings import die


class PdfReader(PdfReaderBase):
    def __init__(
        self,
        stream: Union[StrByteType, Path],
        strict: bool = False,
        password: Union[str, bytes, None] = None,
    ) -> None:
        super().__init__(stream, strict, password)
        assert len(self.pages) > 0
        mediabox = self.pages[0].mediabox
        self.size = Rectangle(mediabox.width, mediabox.height)
        self.size_guessed = False


size_keywords = (
    b"DocumentMedia",
    b"PageBoundingBox",
    b"HiResBoundingBox",
    b"BoundingBox",
)


# FIXME: Store lists of lines, not file offsets.
class PsReader:
    def __init__(self, infile: IO[bytes]) -> None:
        self.infile = infile
        self.headerpos: int = 0
        self.pagescmt: int = 0
        self.endsetup: int = 0
        self.procset_pos: range = range(0, 0)  # pstops procset location
        self.num_pages: int = 0
        self.sizeheaders: list[int] = []
        self.pageptr: list[int] = []
        self.size = None
        self.size_guessed = False

        nesting = 0
        self.infile.seek(0)
        record, next_record, buffer = 0, 0, None
        file_sizes = {}
        for buffer in self.infile:
            next_record += len(buffer)
            if buffer.startswith(b"%%"):
                keyword, value = self.comment(buffer)
                if keyword is not None:
                    # If input paper size is not set, try to read it
                    if (
                        self.headerpos == 0
                        and self.size is None
                        and keyword in size_keywords
                    ):
                        assert value is not None
                        words = value.split(b" ")
                        if keyword == b"DocumentMedia" and len(words) > 2:
                            w = words[1].decode("utf-8", "ignore")
                            h = words[2].decode("utf-8", "ignore")
                            try:
                                file_sizes[keyword] = Rectangle(float(w), float(h))
                            except ValueError:
                                pass
                        elif len(words) == 4:
                            llx = words[0].decode("utf-8", "ignore")
                            lly = words[1].decode("utf-8", "ignore")
                            urx = words[2].decode("utf-8", "ignore")
                            ury = words[3].decode("utf-8", "ignore")
                            try:
                                file_sizes[keyword] = Rectangle(
                                    float(urx) - float(llx), float(ury) - float(lly)
                                )
                            except ValueError:
                                pass
                    if nesting == 0 and keyword == b"Page":
                        self.pageptr.append(record)
                    elif self.headerpos == 0 and (
                        keyword in size_keywords or keyword == b"DocumentPaperSizes"
                    ):
                        self.sizeheaders.append(record)
                    elif self.headerpos == 0 and keyword == b"Pages":
                        self.pagescmt = record
                    elif self.headerpos == 0 and keyword == b"EndComments":
                        self.headerpos = next_record
                    elif keyword in [
                        b"BeginDocument",
                        b"BeginBinary",
                        b"Begself.infile",
                    ]:
                        nesting += 1
                    elif keyword in [b"EndDocument", b"EndBinary", b"EndFile"]:
                        nesting -= 1
                    elif nesting == 0 and keyword == b"EndSetup":
                        self.endsetup = record
                    elif nesting == 0 and keyword == b"BeginProlog":
                        self.headerpos = next_record
                    elif nesting == 0 and buffer == b"%%BeginProcSet: PStoPS":
                        self.procset_pos = range(record, 0)
                    elif (
                        self.procset_pos.start > 0
                        and self.procset_pos.stop == 0
                        and keyword == b"EndProcSet"
                    ):
                        self.procset_pos = range(self.procset_pos.start, next_record)
                    elif nesting == 0 and keyword in [b"Trailer", b"EOF"]:
                        break
            elif self.headerpos == 0:
                self.headerpos = record
            record = next_record

        # If paper size was not already set, and we found a possible size in
        # the file, use it.
        if self.size is None and len(file_sizes) > 0:
            for keyword in size_keywords:
                file_size = file_sizes.get(keyword)
                if (
                    file_size is not None
                    and file_size.width != 0
                    and file_size.height != 0
                ):
                    self.size = file_size
                    if keyword in (b"BoundingBox", b"HiResBoundingBox"):
                        self.size_guessed = True
                    break
        self.num_pages = len(self.pageptr)
        self.pageptr.append(record)
        if self.endsetup == 0 or self.endsetup > self.pageptr[0]:
            self.endsetup = self.pageptr[0]

    # Return comment keyword and value if `line' is a DSC comment
    def comment(self, line: bytes) -> Union[tuple[bytes, bytes], tuple[None, None]]:
        m = re.match(b"%%([^:]+):?\\s+?(.*\\S?)\\s*$", line)
        return (m[1], m[2]) if m else (None, None)


def document_reader(file: IO[bytes], file_type: str) -> Union[PdfReader, PsReader]:
    constructor: Union[type[PdfReader], type[PsReader]]
    if file_type in (".ps", ".eps"):
        constructor = PsReader
    elif file_type == ".pdf":
        constructor = PdfReader
    else:
        die(f"incompatible file type `{file_type}'")
    return constructor(file)
