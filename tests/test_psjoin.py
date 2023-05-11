from pathlib import Path
from typing import List, Tuple

from pytest import mark, CaptureFixture

from testutils import compare_strings, compare_bytes
from psutils.psjoin import psjoin

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

def run_psjoin(args: List[str], file_type: str, datafiles: Path, capsysbinary: CaptureFixture[bytes], expected_file: Path) -> None:
    psjoin(args)
    if file_type == '.pdf':
        compare_bytes(capsysbinary.readouterr().out, datafiles / Path('output').with_suffix(file_type), expected_file.with_suffix(file_type))
    else:
        compare_strings(capsysbinary.readouterr().out.decode('utf-8'), datafiles / Path('output').with_suffix(file_type), expected_file.with_suffix(file_type))

@mark.files(
    FIXTURE_DIR / 'a4-1',
    FIXTURE_DIR / 'psjoin' / 'psjoin-1-2-expected',
)
def test_psjoin_1_2(capsysbinary: CaptureFixture[bytes], files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    run_psjoin(
        [str(test_file.with_suffix(file_type)), str(test_file.with_suffix(file_type))],
        file_type, datafiles, capsysbinary, expected_file,
    )

@mark.files(
    FIXTURE_DIR / 'a4-1',
    FIXTURE_DIR / 'psjoin' / 'psjoin-1-2-even-expected',
)
def test_psjoin_1_2_even(capsysbinary: CaptureFixture[bytes], files: Tuple[Path, ...], file_type: str) -> None:
    datafiles, test_file, expected_file = files
    run_psjoin(
        [str(test_file.with_suffix(file_type)), str(test_file.with_suffix(file_type)), '--even'],
        file_type, datafiles, capsysbinary, expected_file,
    )

@mark.files(
    FIXTURE_DIR / 'a4-1.ps',
    FIXTURE_DIR / 'psjoin' / 'psjoin-1-2-nostrip-expected.ps',
)
def test_psjoin_1_2_nostrip(capsysbinary: CaptureFixture[bytes], files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    run_psjoin(
        [str(test_file), str(test_file), '--nostrip'],
        '.ps', datafiles, capsysbinary, expected_file,
    )

@mark.files(
    FIXTURE_DIR / 'a4-1.ps',
    FIXTURE_DIR / 'psjoin' / 'psjoin-1-2-save-expected.ps',
)
def test_psjoin_1_2_save(capsysbinary: CaptureFixture[bytes], files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    run_psjoin(
        [str(test_file), str(test_file), '--save'],
        '.ps', datafiles, capsysbinary, expected_file,
    )
