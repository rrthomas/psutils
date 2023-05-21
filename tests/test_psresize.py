from pathlib import Path

from testutils import file_test, make_tests, Case, GeneratedInput
from psutils.command.psresize import psresize

pytestmark = make_tests(
    psresize,
    Path(__file__).parent.resolve() / "test-files",
    Case(
        "20-A4",
        ["-p", "a4"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-A3",
        ["-p", "a3"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-A5",
        ["-p", "a5"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-Letter",
        ["-p", "letter"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-A5in-A4",
        ["-p", "a4"],
        GeneratedInput("a5", 20),
    ),
    Case(
        "20-A3in-A4",
        ["-p", "a4"],
        GeneratedInput("a3", 20),
    ),
)
test_psresize = file_test
