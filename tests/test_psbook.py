from pathlib import Path
from typing import Tuple

import pytest
from pytest import CaptureFixture

from testutils import file_test
from psutils.psbook import main as psbook

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

@pytest.mark.files(
    FIXTURE_DIR / 'a4-3',
    FIXTURE_DIR / 'psbook' / 'psbook-3-expected',
)
def test_psbook_3(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psbook, [str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-3',
    FIXTURE_DIR / 'psbook' / 'psbook-3-signature-4-expected',
)
def test_psbook_3_signature_4(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psbook, ['-s', '4', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psbook' / 'psbook-20-expected',
)
def test_psbook_20(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psbook, [str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psbook' / 'psbook-20-signature-4-expected',
)
def test_psbook_20_signature_4(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psbook, ['-s', '4', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'psbook' / 'psbook-invalid-signature-size-expected-stderr.txt',
)
def test_psbook_invalid_signature_size(capsys: CaptureFixture[str], files: Tuple[Path, ...]) -> None:
    datafiles, expected_stderr = files
    file_test(psbook, ['-s', '3', 'foo'], datafiles, None, capsys, expected_stderr, 1)

@pytest.mark.files(
    FIXTURE_DIR / 'a4-11',
    FIXTURE_DIR / 'psbook' / 'psbook-texlive-expected',
    FIXTURE_DIR / 'psbook' / 'psbook-texlive-expected-stderr.txt',
)
def test_psbook_texlive(capsys: CaptureFixture[str], files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file, expected_stderr = files
    file_test(psbook, ['-s4', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type), capsys, expected_stderr)
