from pathlib import Path
from typing import Tuple

from pytest import mark, CaptureFixture

from testutils import file_test, compare_text_files
from psutils.extractres import extractres
from psutils.includeres import includeres

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

@mark.files(
    FIXTURE_DIR / 'a4-1.ps',
    FIXTURE_DIR / 'extractres-and-includeres' / 'extractres-expected.ps',
)
@mark.datafiles(
    FIXTURE_DIR / 'extractres-and-includeres' / 'ISO-8859-1Encoding-expected.enc',
    FIXTURE_DIR / 'extractres-and-includeres' / 'a2ps-a2ps-hdr2.02-expected.ps',
    FIXTURE_DIR / 'extractres-and-includeres' / 'a2ps-black+white-Prolog2.01-expected.ps',
)
def test_extractres(files: Tuple[Path, ...], capsys: CaptureFixture[str]) -> None:
    datafiles = file_test(extractres, capsys, [], files, '.ps')
    compare_text_files(datafiles / 'ISO-8859-1Encoding.enc', datafiles / 'ISO-8859-1Encoding-expected.enc')
    compare_text_files(datafiles / 'a2ps-a2ps-hdr2.02.ps', datafiles / 'a2ps-a2ps-hdr2.02-expected.ps')
    compare_text_files(datafiles / 'a2ps-black+white-Prolog2.01.ps', datafiles / 'a2ps-black+white-Prolog2.01-expected.ps')

@mark.files(
    FIXTURE_DIR / 'extractres-and-includeres' / 'extractres-expected.ps',
    FIXTURE_DIR / 'extractres-and-includeres' / 'includeres-expected.ps',
)
@mark.datafiles(
    FIXTURE_DIR / 'extractres-and-includeres' / 'ISO-8859-1Encoding.enc',
    FIXTURE_DIR / 'extractres-and-includeres' / 'a2ps-a2ps-hdr2.02.ps',
    FIXTURE_DIR / 'extractres-and-includeres' / 'a2ps-black+white-Prolog2.01.ps',
)
def test_includeres(files: Tuple[Path, ...], capsys: CaptureFixture[str]) -> None:
    file_test(includeres, capsys, [], files, '.ps')
