from pathlib import Path

from testutils import file_test, make_tests, Case, GeneratedInput
from psutils.command.psselect import psselect

pytestmark = make_tests(
    psselect,
    Path(__file__).parent.resolve() / "test-files",
    Case(
        "odd",
        ["-o"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "even",
        ["-e"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "reverse",
        ["-r"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "even-reverse",
        ["-e", "-r"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "positive-range",
        ["--pages", "1-5"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "negative-range",
        ["-p", "_5-_1"],
        GeneratedInput("a4", 20),
    ),
    # Test psselect range going from positive to negative
    Case(
        "positive-negative-range",
        ["-R", "2-_2"],
        GeneratedInput("a4", 20),
    ),
    # Test psselect with short option and complex pagerange
    Case(
        "options-and-complex-pagerange",
        ["-o", "-p4-16,_3-_1"],
        GeneratedInput("a4", 20),
    ),
    # Test psselect with individual pages and ranges with -p
    Case(
        "individual-pages-and-dash-p",
        ["-p1,3,5,2,4,6,8-10,19"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "invalid-pagerange",
        ["-p", "1-5"],
        GeneratedInput("a4", 1),
        2,
    ),
    Case(
        "texlive",
        ["5-15"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "psnup-texlive",
        ["--pages", "1-18"],
        GeneratedInput("a4", 20),
    ),
)
test_psselect = file_test
