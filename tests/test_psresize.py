from pathlib import Path
from typing import List, Tuple

from pytest import mark, param, CaptureFixture

from testutils import file_test
from psutils.psresize import psresize

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


@mark.parametrize(
    "args",
    [
        param(args, marks=mark.files(*files))
        for (args, *files) in [
            (
                ["-P", "a4", "-p", "a4"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psresize" / "psresize-20-A4-expected",
            ),
            (
                ["-P", "a4", "-p", "a3"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psresize" / "psresize-20-A3-expected",
            ),
            (
                ["-P", "a4", "-p", "a5"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psresize" / "psresize-20-A5-expected",
            ),
            (
                ["-P", "a4", "-p", "letter"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psresize" / "psresize-20-Letter-expected",
            ),
            (
                ["-P", "a5", "-p", "a4"],
                FIXTURE_DIR / "a5-20",
                FIXTURE_DIR / "psresize" / "psresize-20-A5in-A4-expected",
            ),
            (
                ["-P", "a3", "-p", "a4"],
                FIXTURE_DIR / "a3-20",
                FIXTURE_DIR / "psresize" / "psresize-20-A3in-A4-expected",
            ),
        ]
    ],
)
def test_psresize(
    args: List[str],
    capsys: CaptureFixture[str],
    files: Tuple[Path, ...],
    file_type: str,
) -> None:
    file_test(psresize, capsys, args, files, file_type)
