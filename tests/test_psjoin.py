from contextlib import redirect_stdout
from pathlib import Path
from typing import List

from testutils import make_tests, file_test, Case, GeneratedInput
from psutils.command.psjoin import psjoin

FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


def psjoin_to_file(args: List[str]) -> None:
    output_file = args.pop()
    args.append(args[-1])
    with open(output_file, "w", encoding="utf-8") as f:
        with redirect_stdout(f):
            psjoin(args)


pytestmark = make_tests(
    psjoin_to_file,
    Path(__file__).parent.resolve() / "test-files",
    Case(
        "1-2",
        [],
        GeneratedInput("a4", 1),
    ),
    Case(
        "1-2-even",
        ["--even"],
        GeneratedInput("a4", 1),
    ),
    Case(
        "1-2-nostrip",
        ["--nostrip"],
        GeneratedInput("a4", 1),
    ),
    Case(
        "1-2-save",
        ["--save"],
        GeneratedInput("a4", 1),
    ),
)
test_psjoin_1_2 = file_test
