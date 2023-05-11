from pathlib import Path
from typing import Any, Tuple

import pytest
from pytest import FixtureRequest


def pytest_configure(config: Any) -> None:
    config.addinivalue_line("markers", "files(file, ...): supply test files")


def pytest_generate_tests(metafunc: Any) -> None:
    if "file_type" in metafunc.fixturenames:
        metafunc.parametrize("file_type", [".ps", ".pdf"])


@pytest.fixture
def files(request: FixtureRequest, datafiles: Path) -> Tuple[Path, ...]:
    marks = list(request.node.iter_markers("files"))[0].args
    return tuple([datafiles, *marks])
