from pathlib import Path
from typing import List, Tuple

from pytest import CaptureFixture

from testutils import file_test, make_tests
from psutils.psresize import psresize

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


pytestmark = make_tests(
    psresize,
    FIXTURE_DIR,
    (
        "20-A4",
        ["-P", "a4", "-p", "a4"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-A3",
        ["-P", "a4", "-p", "a3"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-A5",
        ["-P", "a4", "-p", "a5"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-Letter",
        ["-P", "a4", "-p", "letter"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-A5in-A4",
        ["-P", "a5", "-p", "a4"],
        FIXTURE_DIR / "a5-20",
    ),
    (
        "20-A3in-A4",
        ["-P", "a3", "-p", "a4"],
        FIXTURE_DIR / "a3-20",
    ),
)


def test_psresize(
    args: List[str],
    capsys: CaptureFixture[str],
    files: Tuple[Path, ...],
    file_type: str,
    exit_code: int,
    regenerate_expected: bool,
) -> None:
    file_test(psresize, capsys, args, files, file_type, exit_code, regenerate_expected)
