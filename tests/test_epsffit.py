from pathlib import Path
from itertools import combinations
from typing import Callable, List, Iterable

from pytest import CaptureFixture

from testutils import file_test, make_tests, Case
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


# pylint: disable=similarities
def test_epsffit(
    function: Callable[[List[str]], None],
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
