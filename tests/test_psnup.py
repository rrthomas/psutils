from pathlib import Path
from typing import List, Tuple

from pytest import CaptureFixture

from testutils import make_tests, file_test
from psutils.psnup import psnup

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


pytestmark = make_tests(
    psnup,
    FIXTURE_DIR,
    (
        "20-1",
        ["-p", "a4", "-1"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-2",
        ["-p", "a4", "-2"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-3",
        ["-p", "a4", "-3"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-4",
        ["-p", "a4", "-4"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-1-flip",
        ["-p", "a4", "-1", "-f"],  # '-P', 'a4', '-p', '297mmx210mm', '-1'
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-1-inpaper-A4-outpaper-A5",
        ["-P", "a4", "-p", "a5", "-1"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-1-inpaper-A5",
        ["-P", "a5", "-p", "a4", "-1"],
        FIXTURE_DIR / "a5-20",
    ),
    (
        "20-2-inpaper-A5",
        ["-P", "a5", "-p", "a4", "-2"],
        FIXTURE_DIR / "a5-20",
    ),
    (
        "20-3-inpaper-A5",
        ["-P", "a5", "-p", "a4", "-3"],
        FIXTURE_DIR / "a5-20",
    ),
    (
        "20-1-inpaper-A5-outpaper-A5",
        ["-P", "a5", "-p", "a5", "-1"],
        FIXTURE_DIR / "a5-20",
    ),
    (
        "20-3-rotatedleft",
        ["-p", "a4", "-3", "-l"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-3-rotatedright",
        ["-p", "a4", "-3", "-r"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-3-impossible-tolerance",
        ["-p", "a4", "-3", "-t", "0"],
        Path("no-input"),
        1,
    ),
    (
        "20-4-flip",
        ["-p", "a4", "-4", "-f"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-4-border-20",
        ["-p", "a4", "-4", "-b", "20pt"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-4-margin-10",
        ["-p", "a4", "-4", "-m", "10pt"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-4-inpaper-A5",
        ["-P", "a5", "-p", "a4", "-4"],
        FIXTURE_DIR / "a5-20",
    ),
    (
        "20-4-297mmx210mm",
        ["-p", "297mmx210mm", "-4"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-4-columnmajor",
        ["-p", "a4", "-4", "-c"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-4-impossible-border",
        ["-p", "a4", "-4", "-b", "1000pt"],
        Path("no-input"),
        1,
    ),
    (
        "20-4-impossible-margin",
        ["-p", "a4", "-4", "-m", "1000pt"],
        Path("no-input"),
        1,
    ),
    (
        "draw",
        ["-p", "a4", "-4", "--draw=1pt"],
        FIXTURE_DIR / "a4-4-noborder",
    ),
    (
        "texlive",
        ["-pa4", "-2"],
        FIXTURE_DIR / "a4-11",
    ),
    (
        "texlive2",
        ["-pa4", "-18"],
        FIXTURE_DIR / "psselect-texlive-output",
    ),
)


def test_psnup(
    args: List[str],
    capsys: CaptureFixture[str],
    files: Tuple[Path, ...],
    file_type: str,
    exit_code: int,
    regenerate_expected: bool,
) -> None:
    file_test(psnup, capsys, args, files, file_type, exit_code, regenerate_expected)
