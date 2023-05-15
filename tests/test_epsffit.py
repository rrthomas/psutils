from pathlib import Path
from typing import Callable, List

from pytest import CaptureFixture

from testutils import file_test, make_tests, Case
from psutils.epsffit import epsffit

pytestmark = make_tests(
    epsffit,
    Path(__file__).parent.resolve() / "test-files",
    Case(
        "no-options",
        ["100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "aspect",
        ["-a", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "center",
        ["-c", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "maximize",
        ["-m", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "rotate",
        ["-r", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "showpage",
        ["-s", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "center-rotate",
        ["-c", "-r", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "rotate-aspect",
        ["-r", "-a", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "rotate-maximize",
        ["-r", "-m", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "center-rotate-aspect",
        ["-c", "-r", "-a", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "center-rotate-maximize",
        ["-c", "-r", "-m", "100pt", "100pt", "200pt", "300pt"],
        "tiger.eps",
    ),
    Case(
        "center-rotate-aspect-maximize",
        ["-c", "-r", "-a", "-m", "100pt", "100pt", "200pt", "300pt"],
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
    function: Callable[[List[str]], None],
    case: Case,
    datadir: Path,
    capsys: CaptureFixture[str],
    datafiles: Path,
    regenerate_input: bool,
    regenerate_expected: bool,
) -> None:
    file_test(
        function,
        case,
        datadir,
        capsys,
        datafiles,
        ".eps",
        regenerate_input,
        regenerate_expected,
    )
