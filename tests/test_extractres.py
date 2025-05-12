"""extractres tests.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

from pathlib import Path

from pytest import CaptureFixture, mark
from testutils import Case, GeneratedInput, compare_text_files, file_test

from psutils.command.extractres import extractres


FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


@mark.datafiles(
    FIXTURE_DIR / "extractres" / "sample" / "ISO-8859-1Encoding-expected.enc",
    FIXTURE_DIR / "extractres" / "sample" / "a2ps-a2ps-hdr2.02-expected.ps",
    FIXTURE_DIR / "extractres" / "sample" / "a2ps-black+white-Prolog2.01-expected.ps",
)

def test_extractres(
    capsys: CaptureFixture[str],
    datafiles: Path,
    regenerate_input: bool,
    regenerate_expected: bool,
) -> None:
    file_test(
        extractres,
        Case(
            "sample",
            [],
            GeneratedInput("a4", 1),
        ),
        FIXTURE_DIR,
        capsys,
        datafiles,
        ".ps",
        regenerate_input,
        regenerate_expected,
    )
    assert compare_text_files(
        capsys,
        datafiles / "ISO-8859-1Encoding.enc",
        datafiles / "ISO-8859-1Encoding-expected.enc",
    )
    assert compare_text_files(
        capsys,
        datafiles / "a2ps-a2ps-hdr2.02.ps",
        datafiles / "a2ps-a2ps-hdr2.02-expected.ps",
    )
    assert compare_text_files(
        capsys,
        datafiles / "a2ps-black+white-Prolog2.01.ps",
        datafiles / "a2ps-black+white-Prolog2.01-expected.ps",
    )
