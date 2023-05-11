from pathlib import Path
from typing import List, Tuple

from pytest import mark, param, CaptureFixture

from testutils import file_test
from psutils.psnup import psnup

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


@mark.parametrize(
    "args",
    [
        param(args, marks=mark.files(*files))
        for (args, *files) in [
            (
                ["-p", "a4", "-1"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-1-expected",
            ),
            (
                ["-p", "a4", "-2"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-2-expected",
            ),
            (
                ["-p", "a4", "-3"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-3-expected",
            ),
            (
                ["-p", "a4", "-4"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-4-expected",
            ),
            (
                ["-p", "a4", "-1", "-f"],  # '-P', 'a4', '-p', '297mmx210mm', '-1'
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-1-flip-expected",
            ),
            (
                ["-P", "a4", "-p", "a5", "-1"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-1-inpaper-A4-outpaper-A5-expected",
            ),
            (
                ["-P", "a5", "-p", "a4", "-1"],
                FIXTURE_DIR / "a5-20",
                FIXTURE_DIR / "psnup" / "psnup-20-1-inpaper-A5-expected",
            ),
            (
                ["-P", "a5", "-p", "a4", "-2"],
                FIXTURE_DIR / "a5-20",
                FIXTURE_DIR / "psnup" / "psnup-20-2-inpaper-A5-expected",
            ),
            (
                ["-P", "a5", "-p", "a4", "-3"],
                FIXTURE_DIR / "a5-20",
                FIXTURE_DIR / "psnup" / "psnup-20-3-inpaper-A5-expected",
            ),
            (
                ["-P", "a5", "-p", "a5", "-1"],
                FIXTURE_DIR / "a5-20",
                FIXTURE_DIR / "psnup" / "psnup-20-1-inpaper-A5-outpaper-A5-expected",
            ),
            (
                ["-p", "a4", "-3", "-l"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-3-rotatedleft-expected",
            ),
            (
                ["-p", "a4", "-3", "-r"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-3-rotatedright-expected",
            ),
            (
                ["-p", "a4", "-3", "-t", "0"],
                Path("no-input"),
                Path("no-output"),
                FIXTURE_DIR
                / "psnup"
                / "psnup-20-3-impossible-tolerance-expected-stderr.txt",
            ),
            (
                ["-p", "a4", "-4", "-f"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-4-flip-expected",
            ),
            (
                ["-p", "a4", "-4", "-b", "20pt"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-4-border-20-expected",
            ),
            (
                ["-p", "a4", "-4", "-m", "10pt"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-4-margin-10-expected",
            ),
            (
                ["-P", "a5", "-p", "a4", "-4"],
                FIXTURE_DIR / "a5-20",
                FIXTURE_DIR / "psnup" / "psnup-20-4-inpaper-A5-expected",
            ),
            (
                ["-p", "297mmx210mm", "-4"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-4-297mmx210mm-expected",
            ),
            (
                ["-p", "a4", "-4", "-c"],
                FIXTURE_DIR / "a4-20",
                FIXTURE_DIR / "psnup" / "psnup-20-4-columnmajor-expected",
            ),
            (
                ["-p", "a4", "-4", "-b", "1000pt"],
                Path("no-input"),
                Path("no-output"),
                FIXTURE_DIR
                / "psnup"
                / "psnup-20-4-impossible-border-expected-stderr.txt",
            ),
            (
                ["-p", "a4", "-4", "-m", "1000pt"],
                Path("no-input"),
                Path("no-output"),
                FIXTURE_DIR
                / "psnup"
                / "psnup-20-4-impossible-margin-expected-stderr.txt",
            ),
            (
                ["-p", "a4", "-4", "--draw=1pt"],
                FIXTURE_DIR / "a4-4-noborder",
                FIXTURE_DIR / "psnup" / "psnup-draw-expected",
            ),
            (
                ["-pa4", "-2"],
                FIXTURE_DIR / "a4-11",
                FIXTURE_DIR / "psnup" / "psnup-texlive-expected",
                FIXTURE_DIR / "psnup" / "psnup-texlive-expected-stderr.txt",
            ),
        ]
    ],
)
def test_psnup(
    args: List[str],
    capsys: CaptureFixture[str],
    files: Tuple[Path, ...],
    file_type: str,
) -> None:
    file_test(psnup, capsys, args, files, file_type)
