import os
import sys
import subprocess
import re
import difflib
import shutil
from contextlib import ExitStack
from pathlib import Path
from dataclasses import dataclass
from unittest.mock import patch
from typing import Any, Callable, List, Iterator, Optional, Union
from warnings import warn

import pytest
from pytest import CaptureFixture, mark, param
from wand.image import Image  # type: ignore

if sys.version_info[:2] >= (3, 11):
    from contextlib import chdir
else:
    from contextlib import contextmanager

    @contextmanager
    def chdir(path: os.PathLike[str]) -> Iterator[None]:
        old_dir = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(old_dir)


@dataclass
class GeneratedInput:
    paper: str
    pages: int
    border: int = 1


@dataclass
class Case:
    name: str
    args: List[str]
    input: Union[GeneratedInput, str]
    error: Optional[int] = None


def remove_creation_date(lines: List[str]) -> List[str]:
    return [l for l in lines if not re.match(r"(% )?%%CreationDate", l)]


def compare_text_files(
    capsys: CaptureFixture[str],
    output_file: os.PathLike[str],
    expected_file: os.PathLike[str],
) -> bool:
    with ExitStack() as stack:
        out_fd = stack.enter_context(open(output_file, encoding="ascii"))
        exp_fd = stack.enter_context(open(expected_file, encoding="ascii"))
        output_lines = remove_creation_date(out_fd.readlines())
        expected_lines = remove_creation_date(exp_fd.readlines())
        diff = list(
            difflib.unified_diff(
                output_lines, expected_lines, str(output_file), str(expected_file)
            )
        )
        if len(diff) > 0:
            with capsys.disabled():
                sys.stdout.writelines(diff)
        return len(diff) == 0
    return False


def image_to_bytes(image_file: os.PathLike[str]) -> bytes:
    with Image(filename=image_file) as image:
        bytestr = b""
        # FIXME: If comparison fails, save images that differ for debugging
        for i, frame in enumerate(image.sequence):  # pylint: disable=unused-variable
            frame_img = Image(image=frame)
            bytestr += frame_img.make_blob("pnm")
            # frame_img.save(filename=f"{image_file}-{i}.pnm")
        return bytestr
    return b""


def compare_image_files(
    capsys: CaptureFixture[str],
    output_file: os.PathLike[str],
    expected_file: os.PathLike[str],
) -> bool:
    with ExitStack() as stack:
        out_fd = stack.enter_context(open(output_file, "rb"))
        exp_fd = stack.enter_context(open(expected_file, "rb"))
        output = out_fd.read()
        expected = exp_fd.read()
        if output == expected:
            return True
        output_bytes = image_to_bytes(output_file)
        expected_bytes = image_to_bytes(expected_file)
        if output_bytes == expected_bytes:
            with capsys.disabled():
                warn(
                    f"{output_file} not identical to {expected_file} but looks the same"
                )
            return True
    return False


def compare_strings(
    capsys: CaptureFixture[str],
    output: str,
    output_file: os.PathLike[str],
    expected_file: os.PathLike[str],
) -> bool:
    with open(output_file, "w", encoding="ascii") as f:
        f.write(output)
    return compare_text_files(capsys, output_file, expected_file)


def file_test(
    function: Callable[[List[str]], None],
    case: Case,
    fixture_dir: Path,
    capsys: CaptureFixture[str],
    datafiles: Path,
    file_type: str,
    regenerate_input: bool,
    regenerate_expected: bool,
) -> None:
    module_name = function.__name__
    expected_file = fixture_dir / module_name / case.name / "expected"
    expected_stderr = (
        fixture_dir / module_name / case.name / f"expected-stderr-{file_type[1:]}.txt"
    )
    if not os.path.exists(expected_stderr):
        expected_stderr = fixture_dir / module_name / case.name / "expected-stderr.txt"
    if isinstance(case.input, str):
        test_file = fixture_dir / case.input
    else:
        basename = f"{case.input.paper}-{case.input.pages}"
        if case.input.border != 1:
            basename += f"-{case.input.border}"
        test_file = fixture_dir / basename
    if regenerate_input and isinstance(case.input, GeneratedInput):
        make_test_input(
            case.input.paper, case.input.pages, test_file, case.input.border
        )
    output_file = datafiles / "output"
    full_args = [*case.args, str(test_file.with_suffix(file_type)), str(output_file)]
    patched_argv = [module_name, *(sys.argv[1:])]
    with chdir(datafiles):
        correct_output = True
        if case.error is None:
            with patch("sys.argv", patched_argv):
                function(full_args)
            if regenerate_expected:
                shutil.copyfile(output_file, expected_file.with_suffix(file_type))
                correct_output = True
            else:
                comparer = (
                    compare_text_files
                    if file_type in (".ps", ".eps")
                    else compare_image_files
                )
                correct_output = comparer(
                    capsys, output_file, expected_file.with_suffix(file_type)
                )
        else:
            with pytest.raises(SystemExit) as e:
                with patch("sys.argv", patched_argv):
                    function(full_args)
            assert e.value.code == case.error
        if regenerate_expected:
            with open(expected_stderr, "w", encoding="utf-8") as f:
                f.write(capsys.readouterr().err)
            correct_stderr = True
        else:
            correct_stderr = compare_strings(
                capsys,
                capsys.readouterr().err,
                datafiles / "stderr.txt",
                expected_stderr,
            )
        if not (correct_output and correct_stderr):
            bad_results: List[str] = []
            if not correct_output:
                bad_results.append("output")
            if not correct_stderr:
                bad_results.append("stderr")
            raise ValueError(
                f"test {','.join(bad_results)} does not match expected output"
            )


def make_tests(
    function: Callable[..., Any],
    fixture_dir: Path,
    *tests: Case,
) -> Any:
    ids = []
    test_cases = []
    for t in tests:
        ids.append(t.name)
        test_cases.append(t)
    return mark.parametrize(
        "function,case,fixture_dir",
        [
            param(
                function,
                case,
                fixture_dir,
                marks=mark.datafiles,
            )
            for case in test_cases
        ],
        ids=ids,
    )


# Make a test PostScript or PDF file of a given number of pages
# Requires a2ps and ps2pdf
# Simply writes a large page number on each page
def make_test_input(
    paper: str, pages: int, file: Path, border: Optional[int] = 1
) -> None:
    # Configuration
    lines_per_page = 4

    # Produce PostScript
    title = file.stem
    text = ("\n" * lines_per_page).join([str(i + 1) for i in range(pages)])
    subprocess.run(
        [
            "a2ps",
            f"--medium={paper}",
            f"--title={title}",
            f"--lines-per-page={lines_per_page}",
            "--portrait",
            "--columns=1",
            "--rows=1",
            f"--border={border}",
            "--no-header",
            f"--output={file.with_suffix('.ps')}",
        ],
        text=True,
        input=text,
        check=True,
    )

    # Convert to PDF if required
    if file.suffix == ".pdf":
        subprocess.check_call(
            [
                "ps2pdf",
                f"-sPAPERSIZE={paper}",
                f"{file.with_suffix('.ps')}",
                f"{file.with_suffix('.pdf')}",
            ]
        )
        os.remove(f"{file.with_suffix('.ps')}")
