"""PSUtils warning and error routines.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import sys
from typing import Callable, NoReturn, Optional, TextIO, Union
from warnings import warn


# Error messages
def simple_warning(prog: str) -> Callable[..., None]:
    def _warning(
        message: Union[Warning, str],
        category: type[Warning],
        filename: str,
        lineno: int,
        file: Optional[TextIO] = sys.stderr,
        line: Optional[str] = None,
    ) -> None:
        print(f"\n{prog}: {message}", file=file or sys.stderr)

    return _warning


def die(msg: str, code: Optional[int] = 1) -> NoReturn:
    warn(msg)
    sys.exit(code)
