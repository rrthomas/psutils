"""includeres tests.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

from pathlib import Path
from typing import Callable

from pytest import CaptureFixture, mark
from testutils import Case, file_test, make_tests

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
def test_includeres(
    function: Callable[[list[str]], None],
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
