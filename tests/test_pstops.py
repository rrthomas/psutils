from pathlib import Path
from typing import List, Tuple

from pytest import CaptureFixture

from testutils import make_tests, file_test
from psutils.pstops import pstops

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"

pytestmark = make_tests(
    pstops,
    FIXTURE_DIR,
    (
        "offsets",
        ["--specs", "0(100pt,200pt)"],
        FIXTURE_DIR / "a4-1",
    ),
    (
        "negative-offsets",
        ["--specs", "0(-100pt,-200pt)"],
        FIXTURE_DIR / "a4-1",
    ),
    (
        "correct-angles",
        ["-pa4", "--specs", "0L(1w,0)+0R(0,1h)"],
        FIXTURE_DIR / "a5-1",
    ),
    (
        "multiple-pages",
        ["--specs", "2:0(100pt,200pt),1(-200pt,100pt)"],
        FIXTURE_DIR / "a4-2",
    ),
    (
        "multiple-turns-and-flips",
        ["-P", "a4", "--specs", "0LLRVHVHV(700pt,0pt)"],
        FIXTURE_DIR / "a4-1",
    ),
    (
        "invalid-pagespecs",
        ["--specs=foo"],
        FIXTURE_DIR / "a4-1",
        1,
    ),
    (
        "texlive",
        ["-pa4", "--specs", "2:0L@.7(21cm,0)+1L@.7(21cm,14.85cm)"],
        FIXTURE_DIR / "a4-11.ps",
    ),
)


def test_pstops(
    args: List[str],
    capsys: CaptureFixture[str],
    files: Tuple[Path, ...],
    file_type: str,
    exit_code: int,
    regenerate_expected: bool,
) -> None:
    file_test(pstops, capsys, args, files, file_type, exit_code, regenerate_expected)
