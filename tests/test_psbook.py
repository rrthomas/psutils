"""psbook tests.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

from pathlib import Path

from testutils import Case, GeneratedInput, file_test, make_tests

from psutils.command.psbook import psbook


pytestmark = make_tests(
    psbook,
    Path(__file__).parent.resolve() / "test-files",
    Case(
        "3",
        [],
        GeneratedInput("a4", 3),
    ),
    Case(
        "3-signature-4",
        ["-s", "4"],
        GeneratedInput("a4", 3),
    ),
    Case(
        "20",
        [],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-signature-4",
        ["-s", "4"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "invalid-signature-size",
        ["-s", "3"],
        "no-input",
        1,
    ),
    Case(
        "texlive",
        ["-s4"],
        GeneratedInput("a4", 11),
    ),
)
test_psbook = file_test
