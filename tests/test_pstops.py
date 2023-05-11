from pathlib import Path
from typing import List, Tuple

from pytest import mark, param, CaptureFixture

from testutils import file_test
from psutils.pstops import pstops

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


@mark.parametrize(
    "args",
    [
        param(args, marks=mark.files(*files))
        for (args, *files) in [
            (
                ["--specs", "0(100pt,200pt)"],
                FIXTURE_DIR / "a4-1",
                FIXTURE_DIR / "pstops" / "pstops-offsets-expected",
            ),
            (
                ["--specs", "0(-100pt,-200pt)"],
                FIXTURE_DIR / "a4-1",
                FIXTURE_DIR / "pstops" / "pstops-negative-offsets-expected",
            ),
            (
                ["-pa4", "--specs", "0L(1w,0)+0R(0,1h)"],
                FIXTURE_DIR / "a5-1",
                FIXTURE_DIR / "pstops" / "pstops-correct-angles-expected",
            ),
            (
                ["--specs", "2:0(100pt,200pt),1(-200pt,100pt)"],
                FIXTURE_DIR / "a4-2",
                FIXTURE_DIR / "pstops" / "pstops-multiple-pages-expected",
            ),
            (
                ["-P", "a4", "--specs", "0LLRVHVHV(700pt,0pt)"],
                FIXTURE_DIR / "a4-1",
                FIXTURE_DIR / "pstops" / "pstops-multiple-turns-and-flips-expected",
            ),
            (
                ["--specs=foo"],
                FIXTURE_DIR / "a4-1",
                Path("no-output"),
                FIXTURE_DIR / "pstops" / "pstops-invalid-pagespecs-expected-stderr.txt",
            ),
            (
                ["-pa4", "--specs", "2:0L@.7(21cm,0)+1L@.7(21cm,14.85cm)"],
                FIXTURE_DIR / "a4-11.ps",
                FIXTURE_DIR / "pstops" / "pstops-texlive-expected.ps",
                FIXTURE_DIR / "pstops" / "pstops-texlive-expected-stderr.txt",
            ),
        ]
    ],
)
def test_pstops(
    args: List[str],
    capsys: CaptureFixture[str],
    files: Tuple[Path, ...],
    file_type: str,
) -> None:
    file_test(pstops, capsys, args, files, file_type)
