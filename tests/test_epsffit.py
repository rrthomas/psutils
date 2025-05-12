"""epsffit tests.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

from collections.abc import Iterable
from itertools import combinations
from pathlib import Path
from typing import Callable

from pytest import CaptureFixture
from testutils import Case, file_test, make_tests

from psutils.command.epsffit import epsffit


OPTIONS = ["aspect", "center", "maximize", "rotate"]

OPTION_SETS = [
    subset for n in range(len(OPTIONS) + 1) for subset in combinations(OPTIONS, n)
]


def argify(options: Iterable[str]) -> Iterable[str]:
    return [f"-{opt[0]}" for opt in options]


option_cases = []
for opts in OPTION_SETS:
    option_cases.append(
        Case(
            "-".join(opts) or "no-options",
            ["100pt", "100pt", "200pt", "300pt", *argify(opts)],
            "tiger.eps",
        )
    )

pytestmark = make_tests(
    epsffit,
    Path(__file__).parent.resolve() / "test-files",
    *option_cases,
    Case(
        "showpage",
        ["-s", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "h-texlive",
        ["-c", "0", "0", "600", "368"],
        "plot.eps",
    ),
    Case(
        "m-texlive",
        ["-m", "0", "0", "368", "500"],
        "plot.eps",
    ),
    Case(
        "v-texlive",
        ["-c", "0", "0", "500", "400"],
        "plot.eps",
    ),
)


def test_epsffit(
    function: Callable[[list[str]], None],
    case: Case,
    fixture_dir: Path,
    capsys: CaptureFixture[str],
    datafiles: Path,
    regenerate_input: bool,
    regenerate_expected: bool,
) -> None:
    file_test(
        function,
        case,
        fixture_dir,
        capsys,
        datafiles,
        ".eps",
        regenerate_input,
        regenerate_expected,
    )
