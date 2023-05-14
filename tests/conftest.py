from pathlib import Path
from typing import Any, Tuple

import pytest
from pytest import FixtureRequest, Parser


def pytest_configure(config: Any) -> None:
    config.addinivalue_line("markers", "files(file, ...): supply test files")


def pytest_generate_tests(metafunc: Any) -> None:
    if "file_type" in metafunc.fixturenames:
        metafunc.parametrize("file_type", [".ps", ".pdf"])


@pytest.fixture
def files(request: FixtureRequest, datafiles: Path) -> Tuple[Path, ...]:
    marks = list(request.node.iter_markers("files"))[0].args
    return tuple([datafiles, *marks])


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--regenerate-expected",
        action="store_true",
        help="regenerate the expected outputs",
    )


@pytest.fixture
def regenerate_expected(request: FixtureRequest) -> bool:
    opt = request.config.getoption("--regenerate-expected")
    assert isinstance(opt, bool)
    return opt
