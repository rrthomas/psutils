"""
PSUtils document reader classes.
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

from pathlib import Path
import re
from typing import List, Tuple, Union, Type, IO

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


# FIXME: Store lists of lines, not file offsets.
class PsReader:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    def __init__(self, infile: IO[bytes]) -> None:
        self.infile = infile
        self.headerpos: int = 0
        self.pagescmt: int = 0
        self.endsetup: int = 0
        self.procset_pos: range = range(0, 0)  # pstops procset location
        self.num_pages: int = 0
        self.sizeheaders: List[int] = []
        self.pageptr: List[int] = []
        self.size = None

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
                        and self.size is None
                        and keyword == b"DocumentMedia:"
                    ):
                        assert value is not None
                        words = value.split(b" ")
                        if len(words) > 2:
                            w = words[1].decode("utf-8", "ignore")
                            h = words[2].decode("utf-8", "ignore")
                            try:
                                self.size = Rectangle(float(w), float(h))
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
        self.num_pages = len(self.pageptr)
        self.pageptr.append(record)
        if self.endsetup == 0 or self.endsetup > self.pageptr[0]:
            self.endsetup = self.pageptr[0]

    # Return comment keyword and value if `line' is a DSC comment
    def comment(self, line: bytes) -> Union[Tuple[bytes, bytes], Tuple[None, None]]:
        m = re.match(b"%%(\\S+)\\s+?(.*\\S?)\\s*$", line)
        return (m[1], m[2]) if m else (None, None)


def document_reader(file: IO[bytes], file_type: str) -> Union[PdfReader, PsReader]:
    constructor: Union[Type[PdfReader], Type[PsReader]]
    if file_type in (".ps", ".eps"):
        constructor = PsReader
    elif file_type == ".pdf":
        constructor = PdfReader
    else:
        die(f"incompatible file type `{file_type}'")
    return constructor(file)
