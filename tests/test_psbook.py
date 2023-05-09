from pathlib import Path
from typing import List, Tuple

from pytest import mark, param, CaptureFixture

from testutils import file_test
from psutils.psbook import main as psbook

FIXTURE_DIR = Path(__file__).parent.resolve() / 'test-files'

@mark.parametrize(
    'args',
    [param(args, marks=mark.files(*files)) for (args, *files) in [
        ([],
            FIXTURE_DIR / 'a4-3',
            FIXTURE_DIR / 'psbook' / 'psbook-3-expected',
        ),
        (['-s', '4'],
            FIXTURE_DIR / 'a4-3',
            FIXTURE_DIR / 'psbook' / 'psbook-3-signature-4-expected',
        ),
        ([],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psbook' / 'psbook-20-expected',
        ),
        (['-s', '4'],
            FIXTURE_DIR / 'a4-20',
            FIXTURE_DIR / 'psbook' / 'psbook-20-signature-4-expected',
        ),
        (['-s', '3'],
            Path('no-input'),
            Path('no-output'),
            FIXTURE_DIR / 'psbook' / 'psbook-invalid-signature-size-expected-stderr.txt',
        ),
        (['-s4'],
            FIXTURE_DIR / 'a4-11',
            FIXTURE_DIR / 'psbook' / 'psbook-texlive-expected',
            FIXTURE_DIR / 'psbook' / 'psbook-texlive-expected-stderr.txt',
        ),
    ]]
)
def test_psbook(args: List[str], capsys: CaptureFixture[str], files: Tuple[Path, ...], file_type: str) -> None:
    file_test(psbook, capsys, args, files, file_type)
