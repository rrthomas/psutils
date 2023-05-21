"""
PSUtils warning and error routines.
Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import sys
from warnings import warn
from typing import Callable, Optional, Union, Type, NoReturn, TextIO


# Error messages
def simple_warning(prog: str) -> Callable[..., None]:
    def _warning(  # pylint: disable=too-many-arguments
        message: Union[Warning, str],
        category: Type[Warning],  # pylint: disable=unused-argument
        filename: str,  # pylint: disable=unused-argument
        lineno: int,  # pylint: disable=unused-argument
        file: Optional[TextIO] = sys.stderr,
        line: Optional[str] = None,  # pylint: disable=unused-argument
    ) -> None:
        print(f"\n{prog}: {message}", file=file or sys.stderr)

    return _warning


def die(msg: str, code: Optional[int] = 1) -> NoReturn:
    warn(msg)
    sys.exit(code)
