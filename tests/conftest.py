"""Pytest IO Mocker for cli programs and test paramaterizations."""
import pytest


@pytest.fixture
def mock_io(mocker):
    """Simple mocker group for IO fd's."""
    stdin = mocker.patch('sys.stdin', autospec=True)
    stdout = mocker.patch('sys.stdout', autospec=True)
    stderr = mocker.patch('sys.stderr', autospec=True)
    return {"stdin": stdin, "stdout": stdout, "stderr": stderr}


def pytest_generate_tests(metafunc):
    """Generates tests from a scenario meta var.
    A quick port of testscenarios:
    https://pypi.org/project/testscenarios/

    Taken liberally from pytest docs:
    https://docs.pytest.org/en/latest/example/parametrize.html#a-quick-port-of-testscenarios
    """

    idlist = []
    argvalues = []
    for scenario_name, scenario in metafunc.cls.scenarios.items():
        idlist.append(scenario_name)
        argnames, values = [], []
        for name, value in scenario.items():
            argnames.append(name)
            values.append(value)
        argvalues.append(values)
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")
