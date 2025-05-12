"""psjoin tests.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

from contextlib import redirect_stdout
from pathlib import Path

from testutils import Case, GeneratedInput, file_test, make_tests

from psutils.command.psjoin import psjoin


FIXTURE_DIR = Path(__file__).parent.resolve() / "test-files"


def psjoin_to_file(args: list[str]) -> None:
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
test_psjoin = file_test
