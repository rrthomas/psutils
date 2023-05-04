from pathlib import Path
from typing import Tuple

import pytest
from pytest import CaptureFixture

from testutils import file_test
from psutils.psselect import main as psselect
from psutils.psnup import main as psnup # for one test

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-odd-expected',
)
def test_psselect_odd(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psselect, ['-o', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-even-expected',
)
def test_psselect_even(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psselect, ['-e', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-reverse-expected',
)
def test_psselect_reverse(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psselect, ['-r', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-even-reverse-expected',
)
def test_psselect_even_reverse(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psselect, ['-e', '-r', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-positive-range-expected',
)
def test_psselect_positive_range(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psselect, ['--pages', '1-5', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-negative-range-expected',
)
def test_psselect_negative_range(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psselect, ['-p', '_5-_1', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-positive-negative-range-expected',
)
# Test psselect range going from positive to negative
def test_psselect_positive_negative_range(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psselect, ['-R', '2-_2', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-options-and-complex-pagerange-expected',
)
# Test psselect with short option and complex pagerange
def test_psselect_options_and_complex_pagerange(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psselect, ['-o', '-p4-16,_3-_1', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-individual-pages-and-dash-p-expected',
)
# Test psselect with individual pages and ranges with -p
def test_psselect_individual_pages_and_dash_p(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psselect, ['-p1,3,5,2,4,6,8-10,19', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-1',
    FIXTURE_DIR / 'psselect' / 'psselect-invalid-pagerange-expected-stderr.txt',
)
def test_psselect_invalid_pagerange(capsys: CaptureFixture[str], files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_stderr = files
    file_test(psselect, ['-p', '1-5', str(test_file.with_suffix(file_type))], datafiles, None, capsys, expected_stderr, 1)

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-texlive-expected.ps',
    FIXTURE_DIR / 'psselect' / 'psselect-texlive-expected-stderr.txt',
)
def test_psselect_texlive(capsys: CaptureFixture[str], files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file, expected_stderr = files
    file_test(psselect, ['5-15', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type), capsys, expected_stderr)

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psselect' / 'psselect-psnup-texlive-expected.ps',
    FIXTURE_DIR / 'psselect' / 'psselect-psselect-expected-stderr.txt',
    FIXTURE_DIR / 'psselect' / 'psselect-psnup-texlive-expected2.ps',
    FIXTURE_DIR / 'psselect' / 'psselect-psnup-expected-stderr.txt',
)
def test_psselect_psnup_texlive(capsys: CaptureFixture[str], files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file, expected_stderr, expected_file_2, expected_stderr_2 = files
    output_file = file_test(psselect, ['--pages', '1-18', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type), capsys, expected_stderr)
    file_test(psnup, ['-pa4', '-18', str(output_file)], datafiles, expected_file_2.with_suffix(file_type), capsys, expected_stderr_2)
