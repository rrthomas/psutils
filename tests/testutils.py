import os
import sys
import difflib
from contextlib import ExitStack
from pathlib import Path
from contextlib import contextmanager
from typing import Callable, List, Optional, Iterator, Tuple

import pytest
from pytest import CaptureFixture

@contextmanager
def pushd(path: os.PathLike[str]) -> Iterator[None]:
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)

def compare(output_file: os.PathLike[str], expected_file: os.PathLike[str]) -> None:
    with ExitStack() as stack:
        out_fd = stack.enter_context(open(output_file))
        exp_fd = stack.enter_context(open(expected_file))
        output_lines = out_fd.readlines()
        expected_lines = exp_fd.readlines()
        diff = list(difflib.unified_diff(output_lines, expected_lines, str(output_file), str(expected_file)))
        if len(diff) > 0:
            sys.stdout.writelines(diff)
            raise ValueError('test output does not match expected output')

def compare_binary(output_file: os.PathLike[str], expected_file: os.PathLike[str]) -> None:
    with ExitStack() as stack:
        out_fd = stack.enter_context(open(output_file, 'rb'))
        exp_fd = stack.enter_context(open(expected_file, 'rb'))
        output = out_fd.read()
        expected = exp_fd.read()
        if output != expected:
            raise ValueError('test output does not match expected output')

def compare_str(output: str, output_file: os.PathLike[str], expected_file: os.PathLike[str]) -> None:
    with open(output_file, 'w') as fd:
        fd.write(output)
    compare(output_file, expected_file)

def compare_bytes(output: bytes, output_file: os.PathLike[str], expected_file: os.PathLike[str]) -> None:
    with open(output_file, 'wb') as fd:
        fd.write(output)
    compare_binary(output_file, expected_file)

def file_test(function: Callable[[List[str]], None], capsys: CaptureFixture[str], args: List[str], files: Tuple[Path, ...], file_type: str) -> Path:
    datafiles, test_file, expected_file, *more_files = files
    expected_stderr, expected_error = None, None
    if len(more_files) > 0:
        expected_stderr = more_files[0]
    if expected_file == Path('no-output'):
        expected_error = 1
    output_file = datafiles / 'output'
    full_args = [*args, str(test_file.with_suffix(file_type)), str(output_file)]
    with pushd(datafiles):
        if expected_error is None:
            assert expected_file
            function(full_args)
            comparer = compare if file_type == '.ps' else compare_binary
            comparer(output_file, expected_file.with_suffix(file_type))
        else:
            with pytest.raises(SystemExit) as e:
                function(full_args)
            assert e.type == SystemExit
            assert e.value.code == expected_error
        if expected_stderr is not None:
            assert capsys is not None
            compare_str(capsys.readouterr().err, datafiles / 'stderr.txt', expected_stderr)
    return datafiles
