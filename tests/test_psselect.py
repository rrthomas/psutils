from pathlib import Path
from typing import Tuple, List, Callable

from pytest import mark, param, CaptureFixture

from testutils import file_test
from psutils.psselect import psselect
from psutils.psnup import psnup # for one test

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

@mark.parametrize(
    'args',
    [param(args, marks=mark.files(*files)) for (args, *files) in [
        (['-o'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-odd-expected',
        ),
        (['-e'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-even-expected',
        ),
        (['-r'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-reverse-expected',
        ),
        (['-e', '-r'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-even-reverse-expected',
        ),
        (['--pages', '1-5'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-positive-range-expected',
        ),
        (['-p', '_5-_1'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-negative-range-expected',
        ),
        # Test psselect range going from positive to negative
        (['-R', '2-_2'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-positive-negative-range-expected',
        ),
        # Test psselect with short option and complex pagerange
        (['-o', '-p4-16,_3-_1'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-options-and-complex-pagerange-expected',
        ),
        # Test psselect with individual pages and ranges with -p
        (['-p1,3,5,2,4,6,8-10,19'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-individual-pages-and-dash-p-expected',
        ),
        (['-p', '1-5'],
            FIXTURE_DIR / 'a4-1',
            Path('no-output'),
            FIXTURE_DIR / 'psselect' / 'psselect-invalid-pagerange-expected-stderr.txt',
        ),
        (['5-15'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-texlive-expected.ps',
            FIXTURE_DIR / 'psselect' / 'psselect-texlive-expected-stderr.txt',
        ),
        (['--pages', '1-18'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psselect' / 'psselect-psnup-texlive-expected',
            FIXTURE_DIR / 'psselect' / 'psselect-psselect-expected-stderr.txt',
        ),
    ]],
)
def test_psselect(capsys: CaptureFixture[str], args: List[str], files: Tuple[Path, ...], file_type: str) -> None:
    file_test(psselect, capsys, args, files, file_type)

@mark.files(
    FIXTURE_DIR / 'psselect-texlive-output',
    FIXTURE_DIR / 'psselect' / 'psselect-psnup-texlive-expected2',
    FIXTURE_DIR / 'psselect' / 'psselect-psnup-expected-stderr.txt',
)
def test_psnup_texlive(capsys: CaptureFixture[str], files: Tuple[Path, ...], file_type: str) -> None:
    file_test(psnup, capsys, ['-pa4', '-18'], files, file_type)
