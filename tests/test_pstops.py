from pathlib import Path
from typing import Tuple

import pytest
from pytest import CaptureFixture

from testutils import file_test
from psutils.pstops import main as pstops

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

@pytest.mark.files(
    FIXTURE_DIR / 'a4-1',
    FIXTURE_DIR / 'pstops' / 'pstops-offsets-expected',
)
def test_pstops_offsets(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(pstops, ['--specs', '0(100pt,200pt)', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-1',
    FIXTURE_DIR / 'pstops' / 'pstops-negative-offsets-expected',
)
def test_pstops_negative_offsets(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(pstops, ['--specs', '0(-100pt,-200pt)', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a5-1',
    FIXTURE_DIR / 'pstops' / 'pstops-correct-angles-expected',
)
def test_pstops_correct_angles(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(pstops, ['-pa4', '--specs', '0L(1w,0)+0R(0,1h)', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-2',
    FIXTURE_DIR / 'pstops' / 'pstops-multiple-pages-expected',
)
def test_pstops_multiple_pages(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(pstops, ['--specs', '2:0(100pt,200pt),1(-200pt,100pt)', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-1',
    FIXTURE_DIR / 'pstops' / 'pstops-multiple-turns-and-flips-expected',
)
def test_pstops_multiple_turns_and_flips(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(pstops, ['-P', 'a4', '--specs', '0LLRVHVHV(700pt,0pt)', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-1',
    FIXTURE_DIR / 'pstops' / 'pstops-invalid-pagespecs-expected-stderr.txt',
)
def test_pstops_invalid_pagespecs(capsys: CaptureFixture[str], files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_stderr = files
    file_test(pstops, ['--specs=foo', str(test_file.with_suffix(file_type))], datafiles, None, capsys, expected_stderr, 1)

@pytest.mark.files(
    FIXTURE_DIR / 'a4-11.ps',
    FIXTURE_DIR / 'pstops' / 'pstops-texlive-expected.ps',
    FIXTURE_DIR / 'pstops' / 'pstops-texlive-expected-stderr.txt',
)
def test_pstops_texlive(capsys: CaptureFixture[str], files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file, expected_stderr = files
    file_test(pstops, ['-pa4', '--specs', '2:0L@.7(21cm,0)+1L@.7(21cm,14.85cm)', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type), capsys, expected_stderr)
