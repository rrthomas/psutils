import os
import sys
import difflib
import shutil
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, Callable, List, Iterator, Tuple, Optional, Union

import pytest
from pytest import CaptureFixture, mark, param


@contextmanager
def pushd(path: os.PathLike[str]) -> Iterator[None]:
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


def compare_text_files(
    output_file: os.PathLike[str], expected_file: os.PathLike[str]
) -> None:
    with ExitStack() as stack:
        out_fd = stack.enter_context(open(output_file, encoding="ascii"))
        exp_fd = stack.enter_context(open(expected_file, encoding="ascii"))
        output_lines = out_fd.readlines()
        expected_lines = exp_fd.readlines()
        diff = list(
            difflib.unified_diff(
                output_lines, expected_lines, str(output_file), str(expected_file)
            )
        )
        if len(diff) > 0:
            sys.stdout.writelines(diff)
            raise ValueError("test output does not match expected output")


def compare_binary_files(
    output_file: os.PathLike[str], expected_file: os.PathLike[str]
) -> None:
    with ExitStack() as stack:
        out_fd = stack.enter_context(open(output_file, "rb"))
        exp_fd = stack.enter_context(open(expected_file, "rb"))
        output = out_fd.read()
        expected = exp_fd.read()
        if output != expected:
            raise ValueError("test output does not match expected output")


def compare_strings(
    output: str, output_file: os.PathLike[str], expected_file: os.PathLike[str]
) -> None:
    with open(output_file, "w", encoding="ascii") as fd:
        fd.write(output)
    compare_text_files(output_file, expected_file)


def compare_bytes(
    output: bytes, output_file: os.PathLike[str], expected_file: os.PathLike[str]
) -> None:
    with open(output_file, "wb") as fd:
        fd.write(output)
    compare_binary_files(output_file, expected_file)


def file_test(
    function: Callable[[List[str]], None],
    capsys: CaptureFixture[str],
    args: List[str],
    files: Tuple[Path, ...],
    file_type: str,
    expected_error: Optional[int],
    regenerate_expected: bool,
) -> Path:
    datafiles, test_file, expected_file, expected_stderr = files
    output_file = datafiles / "output"
    full_args = [*args, str(test_file.with_suffix(file_type)), str(output_file)]
    with pushd(datafiles):
        if expected_error is None:
            assert expected_file is not None
            function(full_args)
            if regenerate_expected:
                shutil.copyfile(output_file, expected_file.with_suffix(file_type))
            else:
                comparer = (
                    compare_text_files if file_type == ".ps" else compare_binary_files
                )
                comparer(output_file, expected_file.with_suffix(file_type))
        else:
            with pytest.raises(SystemExit) as e:
                function(full_args)
            assert e.type == SystemExit
            assert e.value.code == expected_error
        if regenerate_expected:
            with open(expected_stderr, "w", encoding="utf-8") as fd:
                fd.write(capsys.readouterr().err)
        else:
            compare_strings(
                capsys.readouterr().err, datafiles / "stderr.txt", expected_stderr
            )
    return datafiles


def make_tests(
    function: Callable[..., Any],
    fixture_dir: Path,
    *tests: Union[
        Tuple[str, List[str], Path], Tuple[str, List[str], Path, Optional[int]]
    ],
) -> Any:
    module_name = function.__name__
    ids = []
    test_datas = []
    for id_, args, input_, *exit_code in tests:
        ids.append(id_)
        test_datas.append(
            (
                args,
                [
                    input_,
                    fixture_dir / module_name / id_ / "expected",
                    fixture_dir / module_name / id_ / "expected-stderr.txt",
                ],
                exit_code[0] if len(exit_code) > 0 else None,
            )
        )
    return mark.parametrize(
        "args,exit_code",
        [
            (param(args, exit_code, marks=mark.files(*files)))
            for (args, files, exit_code) in test_datas
        ],
        ids=ids,
    )
