from pathlib import Path
from typing import Tuple

import pytest
from pytest import CaptureFixture

from testutils import file_test
from psutils.psnup import main as psnup

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-1-expected',
)
def test_psnup_20_1(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-1', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-2-expected',
)
def test_psnup_20_2(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-2', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-3-expected',
)
def test_psnup_20_3(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-3', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-4-expected',
)
def test_psnup_20_4(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-4', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-1-flip-expected',
)
def test_psnup_20_1_flip(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-1', '-f', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))
    #file_test(psnup, ['-P', 'a4', '-p', '297mmx210mm', '-1', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-1-inpaper-A4-outpaper-A5-expected',
)
def test_psnup_20_1_inpaper_A4_outpaper_A5(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-P', 'a4', '-p', 'a5', '-1', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a5-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-1-inpaper-A5-expected',
)
def test_psnup_20_1_inpaper_A5(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-P', 'a5', '-p', 'a4', '-1', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a5-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-2-inpaper-A5-expected',
)
def test_psnup_20_2_inpaper_A5(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-P', 'a5', '-p', 'a4', '-2', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a5-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-3-inpaper-A5-expected',
)
def test_psnup_20_3_inpaper_A5(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-P', 'a5', '-p', 'a4', '-3', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a5-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-1-inpaper-A5-outpaper-A5-expected',
)
def test_psnup_20_1_inpaper_A5_outpaper_A5(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-P', 'a5', '-p', 'a5', '-1', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-3-rotatedleft-expected',
)
def test_psnup_20_3_rotatedleft(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-3', '-l', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-3-rotatedright-expected',
)
def test_psnup_20_3_rotatedright(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-3', '-r', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'psnup' / 'psnup-20-3-impossible-tolerance-expected-stderr.txt',
)
def test_psnup_20_3_impossible_tolerance(capsys: CaptureFixture[str], files: Tuple[Path, ...]) -> None:
    datafiles, expected_stderr = files
    file_test(psnup, ['-p', 'a4', '-3', '-t', '0', 'foo'], datafiles, None, capsys, expected_stderr, 1)

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-4-flip-expected',
)
def test_psnup_20_4_flip(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-4', '-f', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-4-border-20-expected',
)
def test_psnup_20_4_border_20(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-4', '-b', '20pt', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-4-margin-10-expected',
)
def test_psnup_20_4_margin_10(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-4', '-m', '10pt', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a5-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-4-inpaper-A5-expected',
)
def test_psnup_20_4_inpaper_A5(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-P', 'a5', '-p', 'a4', '-4', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-4-297mmx210mm-expected',
)
def test_psnup_20_4_297mmx210mm(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', '297mmx210mm', '-4', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-20',
    FIXTURE_DIR / 'psnup' / 'psnup-20-4-columnmajor-expected',
)
def test_psnup_20_4_columnmajor(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-4', '-c', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'psnup' / 'psnup-20-4-impossible-border-expected-stderr.txt',
)
def test_psnup_20_4_impossible_border(capsys: CaptureFixture[str], files: Tuple[Path, ...]) -> None:
    datafiles, expected_stderr = files
    file_test(psnup, ['-p', 'a4', '-4', '-b', '1000pt', 'foo'], datafiles, None, capsys, expected_stderr, 1)

@pytest.mark.files(
    FIXTURE_DIR / 'psnup' / 'psnup-20-4-impossible-margin-expected-stderr.txt',
)
def test_psnup_20_4_impossible_margin(capsys: CaptureFixture[str], files: Tuple[Path, ...]) -> None:
    datafiles, expected_stderr = files
    file_test(psnup, ['-p', 'a4', '-4', '-m', '1000pt', 'foo'], datafiles, None, capsys, expected_stderr, 1)

@pytest.mark.files(
    FIXTURE_DIR / 'a4-4-noborder',
    FIXTURE_DIR / 'psnup' / 'psnup-draw-expected',
)
def test_psnup_draw(files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    file_test(psnup, ['-p', 'a4', '-4', '--draw=1pt', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type))

@pytest.mark.files(
    FIXTURE_DIR / 'a4-11',
    FIXTURE_DIR / 'psnup' / 'psnup-texlive-expected',
    FIXTURE_DIR / 'psnup' / 'psnup-texlive-expected-stderr.txt',
)
def test_psnup_texlive(capsys: CaptureFixture[str], files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file, expected_stderr = files
    file_test(psnup, ['-pa4', '-2', str(test_file.with_suffix(file_type))], datafiles, expected_file.with_suffix(file_type), capsys, expected_stderr)
