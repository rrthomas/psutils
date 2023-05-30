from typing import Any

from pytest import FixtureRequest, Parser, fixture


def pytest_generate_tests(metafunc: Any) -> None:
    if "file_type" in metafunc.fixturenames:
        metafunc.parametrize("file_type", [".ps", ".pdf"])


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--regenerate-expected",
        action="store_true",
        help="regenerate the expected outputs",
    )
    parser.addoption(
        "--regenerate-input",
        action="store_true",
        help="regenerate the inputs",
    )


@fixture
def regenerate_expected(request: FixtureRequest) -> bool:
    opt = request.config.getoption("--regenerate-expected")
    assert isinstance(opt, bool)
    return opt


@fixture
def regenerate_input(request: FixtureRequest) -> bool:
    opt = request.config.getoption("--regenerate-input")
    assert isinstance(opt, bool)
    return opt
