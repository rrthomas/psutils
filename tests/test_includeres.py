from pathlib import Path
from typing import Callable, List

from pytest import mark, CaptureFixture

from testutils import file_test, make_tests, Case
from psutils.command.includeres import includeres

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"

pytestmark = make_tests(
    includeres,
    FIXTURE_DIR,
    Case(
        "sample",
        [],
        str(FIXTURE_DIR / "extractres" / "sample" / "expected.ps"),
    ),
)


@mark.datafiles(
    FIXTURE_DIR / "includeres" / "sample" / "ISO-8859-1Encoding.enc",
    FIXTURE_DIR / "includeres" / "sample" / "a2ps-a2ps-hdr2.02.ps",
    FIXTURE_DIR / "includeres" / "sample" / "a2ps-black+white-Prolog2.01.ps",
)
# pylint: disable=similarities
def test_includeres(
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
        ".ps",
        regenerate_input,
        regenerate_expected,
    )
