from pathlib import Path
from typing import List, Tuple

from pytest import mark, param, CaptureFixture

from testutils import file_test
from psutils.epsffit import epsffit

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


@mark.parametrize(
    "args",
    [
        param(args, marks=mark.files(*files))
        for (args, *files) in [
            (
                ["100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-expected.ps",
            ),
            (
                ["-a", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-aspect-expected.ps",
            ),
            (
                ["-c", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-center-expected.ps",
            ),
            (
                ["-m", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-maximize-expected.ps",
            ),
            (
                ["-r", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-rotate-expected.ps",
            ),
            (
                ["-s", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-showpage-expected.ps",
            ),
            (
                ["-c", "-r", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-center-rotate-expected.ps",
            ),
            (
                ["-r", "-a", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-rotate-aspect-expected.ps",
            ),
            (
                ["-r", "-m", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-rotate-maximize-expected.ps",
            ),
            (
                ["-c", "-r", "-a", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-center-rotate-aspect-expected.ps",
            ),
            (
                ["-c", "-r", "-m", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-center-rotate-maximize-expected.ps",
            ),
            (
                ["-c", "-r", "-a", "-m", "100pt", "100pt", "200pt", "300pt"],
                FIXTURE_DIR / "tiger.eps",
                FIXTURE_DIR
                / "epsffit"
                / "epsffit-center-rotate-aspect-maximize-expected.ps",
            ),
            (
                ["-c", "0", "0", "600", "368"],
                FIXTURE_DIR / "plot.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-h-texlive-expected.ps",
            ),
            (
                ["-m", "0", "0", "368", "500"],
                FIXTURE_DIR / "plot.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-m-texlive-expected.ps",
            ),
            (
                ["-c", "0", "0", "500", "400"],
                FIXTURE_DIR / "plot.eps",
                FIXTURE_DIR / "epsffit" / "epsffit-v-texlive-expected.ps",
            ),
        ]
    ],
)
def test_epsffit(
    args: List[str], capsys: CaptureFixture[str], files: Tuple[Path, ...]
) -> None:
    file_test(epsffit, capsys, args, files, ".eps")
