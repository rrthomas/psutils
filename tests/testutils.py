import os
import sys
import difflib
from contextlib import ExitStack
from pathlib import Path
from contextlib import contextmanager
from typing import Callable, List, Optional, Iterator

import pytest
from pytest import CaptureFixture

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

def file_test(
        test_function: Callable[[List[str]], None],
        args: List[str],
        datafiles: Path,
        expected_file: Optional[os.PathLike[str]] = None,
        capsys: Optional[CaptureFixture[str]] = None,
        expected_stderr: Optional[os.PathLike[str]] = None,
        expected_error: Optional[int] = None,
) -> Path:
    output_file = datafiles / 'output'
    if expected_error is None:
        assert expected_file
        test_function([*args, str(output_file)])
        if Path(expected_file).suffix == '.ps':
            compare(output_file, expected_file)
        else:
            compare_binary(output_file, expected_file)
    else:
        with pytest.raises(SystemExit) as e:
            test_function([*args, str(output_file)])
        assert e.type == SystemExit
        assert e.value.code == expected_error
    if expected_stderr is not None:
        assert capsys is not None
        compare_str(capsys.readouterr().err, datafiles / 'stderr.txt', expected_stderr)
    return output_file

@contextmanager
def pushd(path: os.PathLike[str]) -> Iterator[None]:
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)
