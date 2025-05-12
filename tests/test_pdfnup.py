"""pdfnup tests.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

from pathlib import Path
from typing import Callable

from pytest import CaptureFixture
from testutils import Case, file_test, make_tests

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
        ".pdf",
        regenerate_input,
        regenerate_expected,
    )
