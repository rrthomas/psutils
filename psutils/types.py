"""PSUtils basic types.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

from dataclasses import dataclass
from typing import NamedTuple

from .warnings import die


@dataclass
class Rectangle:
    width: float
    height: float

    def __str__(self) -> str:
        return f"{self.width:n}x{self.height:n} pt"


@dataclass
class Range:
    start: int
    end: int
    text: str


class Offset(NamedTuple):
    x: float
    y: float


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


class PageList:
    def __init__(
        self,
        total_pages: int,
        pagerange: list[Range],
        reverse: bool,
        odd: bool,
        even: bool,
    ) -> None:
        self.pages: list[int] = []
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
