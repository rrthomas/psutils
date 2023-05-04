from pathlib import Path
from typing import Tuple

import pytest

from testutils import file_test
from psutils.psresize import main as psresize

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psresize' / 'psresize-20-A4-expected',
)
def test_psresize_20_A4(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psresize, ['-P', 'a4', '-p', 'a4', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psresize' / 'psresize-20-A3-expected',
)
def test_psresize_20_A3(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psresize, ['-P', 'a4', '-p', 'a3', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psresize' / 'psresize-20-A5-expected',
)
def test_psresize_20_A5(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psresize, ['-P', 'a4', '-p', 'a5', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psresize' / 'psresize-20-Letter-expected',
)
def test_psresize_20_Letter(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psresize, ['-P', 'a4', '-p', 'letter', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a5-20',
    FIXTURE_DIR / 'psresize' / 'psresize-20-A5in-A4-expected',
)
def test_psresize_20_A5in_A4(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psresize, ['-P', 'a5', '-p', 'a4', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a3-20',
    FIXTURE_DIR / 'psresize' / 'psresize-20-A3in-A4-expected',
)
def test_psresize_20_A3in_A4(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psresize, ['-P', 'a3', '-p', 'a4', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))
