from pathlib import Path
from typing import List, Tuple

from pytest import CaptureFixture

from testutils import file_test, make_tests
from psutils.epsffit import epsffit

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"

pytestmark = make_tests(
    epsffit,
    FIXTURE_DIR,
    (
        "no-options",
        ["100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "aspect",
        ["-a", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "center",
        ["-c", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "maximize",
        ["-m", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "rotate",
        ["-r", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "showpage",
        ["-s", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "center-rotate",
        ["-c", "-r", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "rotate-aspect",
        ["-r", "-a", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "rotate-maximize",
        ["-r", "-m", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "center-rotate-aspect",
        ["-c", "-r", "-a", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "center-rotate-maximize",
        ["-c", "-r", "-m", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "center-rotate-aspect-maximize",
        ["-c", "-r", "-a", "-m", "100pt", "100pt", "200pt", "300pt"],
        FIXTURE_DIR / "tiger.eps",
    ),
    (
        "h-texlive",
        ["-c", "0", "0", "600", "368"],
        FIXTURE_DIR / "plot.eps",
    ),
    (
        "m-texlive",
        ["-m", "0", "0", "368", "500"],
        FIXTURE_DIR / "plot.eps",
    ),
    (
        "v-texlive",
        ["-c", "0", "0", "500", "400"],
        FIXTURE_DIR / "plot.eps",
    ),
)


def test_epsffit(
    args: List[str],
    capsys: CaptureFixture[str],
    files: Tuple[Path, ...],
    exit_code: int,
    regenerate_expected: bool,
) -> None:
    file_test(epsffit, capsys, args, files, ".eps", exit_code, regenerate_expected)
