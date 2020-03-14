"""Unit tests for deployer.deployer module"""
# pylint: disable=too-few-public-methods,too-many-arguments
from copy import deepcopy

from fabric import Result, Connection
from invoke import UnexpectedExit

from deployer import deployer
from deployer.models import Command
from deployer.cli import DEFAULT_CONFIG


class TestGetCommand:
    """Unit test scenarios for deployer.deployer.get_command"""

    scenarios = {
        "invalid prompts": {
            "user_response": ["x\n", "n\n"],
            "expected_output": None,
            "expected_result": False,
        },
        "prompt continue": {
            "user_response": [
                "yes\n",
                "A simple directory check: \n",
                "pwd\n"
            ],
            "output": "A simple directory check: pwd",
            "result": True,
        }
    }

    @staticmethod
    def test_get_command(mock_io, user_response, output, result):
        """when get_command is called it:
        * should not raise errors
        * should prompt if another command should be entered
            * repeat this prompt until a valid answer is given
        * return (None, False) if no command needed
        * return (<str>, True) if a command is needed
        """

        try:
            mock_io["stdin"].readline.side_effect = user_response
            actual = deployer.get_command()
            assert isinstance(actual[1], bool), \
                "deployer.get_command() should return a response bool flag"
            assert actual[1] == result, \
                f"Actual flag ({actual[1]}) != Expected ({result})"
            if actual[1]:
                assert isinstance(actual[0], (Command, ))
                assert actual[0].desc + actual[0].command == output, \
                    "expected response command has incorrect content"
            else:
                assert actual[0] is None, \
                    "No command should be given if response flag is 'False'"
        except AssertionError as assert_err:
            raise assert_err
        except Exception as err:
            raise AssertionError(f"get_command should not raise errors: {err}")


class TestMakeScript:
    """Unit test scenarios for deployer.deployer.make_script"""
    scenarios = {
        "default empty config": {
            "commands": {},
            "start": None,
            "config": DEFAULT_CONFIG,
            "command_codes": [],
            "added_commands": [(None, False)],
        },

        "default add one command": {
            "commands": {1: Command("pwd", "print working directory", 1, {})},
            "start": 1,
            "config": DEFAULT_CONFIG,
            "command_codes": [0, 0],
            "added_commands": [
                (Command("pwd", "", 1, {}), True),
                (None, False)
            ],
        },

        "add command that fails": {
            "commands": {},
            "start": 1,
            "config": DEFAULT_CONFIG,
            "command_codes": [1],
            "added_commands": [
                (Command("pwd", "print working directory", 1, {}), True),
                (None, False)
            ],
        },

        "unnattended successful run": {
            "commands": {1: Command("pwd", "print working directory", 1, {})},
            "start": 1,
            "config": dict(DEFAULT_CONFIG, unattended=True),
            "command_codes": [0],
            "added_commands": []
        },

        "unnatended failed run": {
            "commands": {
                1: Command("pwd", "print working directory", 1, {0: 2}),
                2: Command("sudo apt update", "update system", 2, {}),
            },
            "start": 1,
            "config": dict(DEFAULT_CONFIG, unattended=True),
            "command_codes": [0, 1],
            "added_commands": []
        }
    }

    @staticmethod
    def test_make_script(mock_io, mocker,
                         commands, start, config,
                         command_codes, added_commands):
        """Whe make script is called it:
        * should not raise errors
        * should run the previously known command FSM from a starting point
        * should have a way to configure that starting point
        * configurably extend the FSM
        """

        try:
            # make all stdin readlines return "yes\n"
            # done so we don't discard any failed commands
            mock_io["stdin"].readline.side_effect = lambda: "yes\n"
            run = mocker.patch.object(Connection, 'run', autospec=True)
            run.side_effect = [
                Result(connection=None, exited=code)
                if code == 0 else
                UnexpectedExit(result=Result(connection=None, exited=code))
                for code in command_codes
            ]
            get_command = mocker.patch('deployer.deployer.get_command')
            get_command.side_effect = added_commands

            expected_commands = deepcopy(commands)
            expected_idx = start
            actual = deployer.make_script(commands, start, config)
            assert actual == (expected_commands, expected_idx), \
                "Command FSM Should match expected FSM"

        except AssertionError as assert_err:
            raise assert_err
        except Exception as err:
            raise AssertionError(f"make_script should not raise errors: {err}")


class TestQueryYesNo:
    """Unit test scenarios for deployer.deployer.query_yes_no"""
