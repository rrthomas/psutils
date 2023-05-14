from pathlib import Path
from typing import Tuple, List

from pytest import CaptureFixture

from testutils import file_test, make_tests
from psutils.psselect import psselect

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


pytestmark = make_tests(
    psselect,
    FIXTURE_DIR,
    (
        "odd",
        ["-o"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "even",
        ["-e"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "reverse",
        ["-r"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "even-reverse",
        ["-e", "-r"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "positive-range",
        ["--pages", "1-5"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "negative-range",
        ["-p", "_5-_1"],
        FIXTURE_DIR / "a4-20",
    ),
    # Test psselect range going from positive to negative
    (
        "positive-negative-range",
        ["-R", "2-_2"],
        FIXTURE_DIR / "a4-20",
    ),
    # Test psselect with short option and complex pagerange
    (
        "options-and-complex-pagerange",
        ["-o", "-p4-16,_3-_1"],
        FIXTURE_DIR / "a4-20",
    ),
    # Test psselect with individual pages and ranges with -p
    (
        "individual-pages-and-dash-p",
        ["-p1,3,5,2,4,6,8-10,19"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "invalid-pagerange",
        ["-p", "1-5"],
        FIXTURE_DIR / "a4-1",
        1,
    ),
    (
        "texlive",
        ["5-15"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "psnup-texlive",
        ["--pages", "1-18"],
        FIXTURE_DIR / "a4-20",
    ),
)


def test_psselect(
    args: List[str],
    capsys: CaptureFixture[str],
    files: Tuple[Path, ...],
    file_type: str,
    exit_code: int,
    regenerate_expected: bool,
) -> None:
    file_test(psselect, capsys, args, files, file_type, exit_code, regenerate_expected)
