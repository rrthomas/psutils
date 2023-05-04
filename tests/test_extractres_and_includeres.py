from pathlib import Path
from typing import Tuple

import pytest

from testutils import file_test, compare, pushd
from psutils.extractres import main as extractres
from psutils.includeres import main as includeres

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

@pytest.mark.files(
    FIXTURE_DIR / 'a4-1.ps',
    FIXTURE_DIR / 'extractres-and-includeres' / 'extractres-expected.ps',
    FIXTURE_DIR / 'extractres-and-includeres' / 'includeres-expected.ps',
    FIXTURE_DIR / 'extractres-and-includeres' / 'ISO-8859-1Encoding-expected.enc',
    FIXTURE_DIR / 'extractres-and-includeres' / 'a2ps-a2ps-hdr2.02-expected.ps',
    FIXTURE_DIR / 'extractres-and-includeres' / 'a2ps-black+white-Prolog2.01-expected.ps',
    FIXTURE_DIR / 'extractres-and-includeres' / 'ISO-8859-1Encoding.enc',
    FIXTURE_DIR / 'extractres-and-includeres' / 'a2ps-a2ps-hdr2.02.ps',
    FIXTURE_DIR / 'extractres-and-includeres' / 'a2ps-black+white-Prolog2.01.ps',
)
def test_extractres_and_includeres(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, extractres_expected_file, includeres_expected_file, encoding_expected_file, header_expected_file, prolog_expected_file, _, _, _ = files
    with pushd(datafiles):
        file_test(extractres, [str(test_file)], datafiles, extractres_expected_file)
        file_test(includeres, [str(extractres_expected_file)], datafiles, includeres_expected_file)
        compare(datafiles / 'ISO-8859-1Encoding.enc', encoding_expected_file)
        compare(datafiles / 'a2ps-a2ps-hdr2.02.ps', header_expected_file)
        compare(datafiles / 'a2ps-black+white-Prolog2.01.ps', prolog_expected_file)