from pathlib import Path

from testutils import file_test, make_tests, Case, GeneratedInput
from psutils.command.psnup import psnup

pytestmark = make_tests(
    psnup,
    Path(__file__).parent.resolve() / "test-files",
    Case(
        "20-1",
        ["-p", "a4", "-1"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-2",
        ["-p", "a4", "-2"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-3",
        ["-p", "a4", "-3"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-4",
        ["-p", "a4", "-4"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-1-flip",
        ["-p", "a4", "-1", "-f"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-1-flipped-dimensions",
        ["-p", "297mmx210mm", "-1"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-1-flipped-dimensions-wrong-inpaper",
        ["-P", "297mmx210mm", "-p", "297mmx210mm", "-1"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-1-inpaper-A4-outpaper-A5",
        ["-p", "a5", "-1"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-1-inpaper-A5",
        ["-p", "a4", "-1"],
        GeneratedInput("a5", 20),
    ),
    Case(
        "20-1-inpaper-A5-set-inpaper",
        ["-P", "a5", "-p", "a4", "-1"],
        GeneratedInput("a5", 20),
    ),
    Case(
        "20-2-inpaper-A5",
        ["-p", "a4", "-2"],
        GeneratedInput("a5", 20),
    ),
    Case(
        "20-3-inpaper-A5",
        ["-p", "a4", "-3"],
        GeneratedInput("a5", 20),
    ),
    Case(
        "20-1-inpaper-A5-outpaper-A5",
        ["-p", "a5", "-1"],
        GeneratedInput("a5", 20),
    ),
    Case(
        "20-3-rotatedleft",
        ["-p", "a4", "-3", "-l"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-3-rotatedright",
        ["-p", "a4", "-3", "-r"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-3-impossible-tolerance",
        ["-p", "a4", "-3", "-t", "0"],
        GeneratedInput("a4", 1),
        1,
    ),
    Case(
        "20-4-flip",
        ["-p", "a4", "-4", "-f"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-4-border-20",
        ["-p", "a4", "-4", "-b", "20pt"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-4-margin-10",
        ["-p", "a4", "-4", "-m", "10pt"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-4-inpaper-A5",
        ["-p", "a4", "-4"],
        GeneratedInput("a5", 20),
    ),
    Case(
        "20-4-297mmx210mm",
        ["-p", "297mmx210mm", "-4"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-4-columnmajor",
        ["-p", "a4", "-4", "-c"],
        GeneratedInput("a4", 20),
    ),
    Case(
        "20-4-impossible-border",
        ["-p", "a4", "-4", "-b", "1000pt"],
        GeneratedInput("a4", 1),
        1,
    ),
    Case(
        "20-4-impossible-margin",
        ["-p", "a4", "-4", "-m", "1000pt"],
        GeneratedInput("a4", 1),
        1,
    ),
    Case(
        "draw",
        ["-p", "a4", "-4", "--draw=1pt"],
        GeneratedInput("a4", 4, 0),
    ),
    Case(
        "texlive",
        ["-pa4", "-2"],
        GeneratedInput("a4", 11),
    ),
    Case(
        "texlive2",
        ["-pa4", "-18"],
        "psselect-texlive-output",
    ),
    # The next 2 tests don't really apply to PDF, but run them anyway to
    # show that the warning is not generated for PDF.
    Case(
        "no-document-media",
        ["-2", "-ptabloid"],
        "no-document-media",
    ),
    Case(
        "no-document-media-explicit-size",
        ["-2", "-P612x792", "-ptabloid"],
        "no-document-media",
    ),
)
test_psnup = file_test
