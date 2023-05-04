from pathlib import Path
from typing import Tuple

import pytest

from testutils import file_test
from psutils.epsffit import main as epsffit

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-expected.ps',
)
def test_epsffit_odd(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-aspect-expected.ps',
)
def test_epsffit_aspect(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-a', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-center-expected.ps',
)
def test_epsffit_center(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-c', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-maximize-expected.ps',
)
def test_epsffit_maximize(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-m', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-rotate-expected.ps',
)
def test_epsffit_rotate(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-r', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-showpage-expected.ps',
)
def test_epsffit_showpage(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-s', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-center-rotate-expected.ps',
)
def test_epsffit_center_rotate(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-c', '-r', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-rotate-aspect-expected.ps',
)
def test_epsffit_rotate_aspect(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-r', '-a', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-rotate-maximize-expected.ps',
)
def test_epsffit_rotate_maximize(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-r', '-m', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-center-rotate-aspect-expected.ps',
)
def test_epsffit_center_rotate_aspect(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-c', '-r', '-a', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-center-rotate-maximize-expected.ps',
)
def test_epsffit_center_rotate_maximize(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-c', '-r', '-m', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'tiger.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-center-rotate-aspect-maximize-expected.ps',
)
def test_epsffit_center_rotate_aspect_maximize(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-c', '-r', '-a', '-m', '100pt', '100pt', '200pt', '300pt', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'plot.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-h-texlive-expected.ps',
)
def test_epsffit_h_texlive(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-c', '0', '0', '600', '368', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'plot.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-m-texlive-expected.ps',
)
def test_epsffit_m_texlive(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-m', '0', '0', '368', '500', str(test_file)], datafiles, expected_file)

@pytest.mark.files(
    FIXTURE_DIR / 'plot.eps',
    FIXTURE_DIR / 'epsffit' / 'epsffit-v-texlive-expected.ps',
)
def test_epsffit_v_texlive(files: Tuple[Path, ...]) -> None:
    datafiles, test_file, expected_file = files
    file_test(epsffit, ['-c', '0', '0', '500', '400', str(test_file)], datafiles, expected_file)
