"""PSUtils warning and error routines.

Copyright (c) Reuben Thomas 2023-2025.
Released under the GPL version 3, or (at your option) any later version.
"""

import sys
from collections.abc import Callable
from typing import NoReturn, TextIO
from warnings import warn


# Error messages
def simple_warning(prog: str) -> Callable[..., None]:
    def _warning(
        message: Warning | str,
        category: type[Warning],
        filename: str,
        lineno: int,
        file: TextIO | None = sys.stderr,
        line: str | None = None,
    ) -> None:
        print(f"\n{prog}: {message}", file=file or sys.stderr)

    return _warning


def die(msg: str, code: int | None = 1) -> NoReturn:
    warn(msg)
    sys.exit(code)
