from pathlib import Path
from typing import List, Tuple

from pytest import CaptureFixture

from testutils import file_test, make_tests
from psutils.psbook import psbook

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


pytestmark = make_tests(
    psbook,
    FIXTURE_DIR,
    (
        "3",
        [],
        FIXTURE_DIR / "a4-3",
    ),
    (
        "3-signature-4",
        ["-s", "4"],
        FIXTURE_DIR / "a4-3",
    ),
    (
        "20",
        [],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "20-signature-4",
        ["-s", "4"],
        FIXTURE_DIR / "a4-20",
    ),
    (
        "invalid-signature-size",
        ["-s", "3"],
        Path("no-input"),
        1,
    ),
    (
        "texlive",
        ["-s4"],
        FIXTURE_DIR / "a4-11",
    ),
)


def test_psbook(
    args: List[str],
    capsys: CaptureFixture[str],
    files: Tuple[Path, ...],
    file_type: str,
    exit_code: int,
    regenerate_expected: bool,
) -> None:
    file_test(psbook, capsys, args, files, file_type, exit_code, regenerate_expected)
