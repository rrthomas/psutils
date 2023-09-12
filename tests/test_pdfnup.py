from pathlib import Path
from typing import List, Callable

from pytest import CaptureFixture

from testutils import file_test, make_tests, Case
from psutils.command.psnup import psnup

pytestmark = make_tests(
    psnup,
    Path(__file__).parent.resolve() / "test-files",
    Case(
        "recursive-links",
        ["-2"],
        "recursive-links",
    ),
)


def test_pdfnup(
    function: Callable[[List[str]], None],
    case: Case,
    fixture_dir: Path,
    capsys: CaptureFixture[str],
    datafiles: Path,
    regenerate_input: bool,
    regenerate_expected: bool,
) -> None:
    file_test(
        function,
        case,
        fixture_dir,
        capsys,
        datafiles,
        ".pdf",
        regenerate_input,
        regenerate_expected,
    )
