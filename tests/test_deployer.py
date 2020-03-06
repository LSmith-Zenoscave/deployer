"""Unit tests for deployer.deployer module"""

from deployer import deployer


class TestGetCommand:  # pylint: disable=too-few-public-methods
    """Unit test scenarios for deployer.deployer.get_command"""

    scenarios = {
        "invalid prompts": {
            "user_response": ["x\n", "n\n"],
            "expected_output": None,
            "expected_result": False,
        },
        "prompt_continue": {
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
                assert actual[0]["desc"] + actual[0]["command"] == output, \
                    "expected response command has incorrect content"
            else:
                assert actual[0] is None, \
                    "No command should be given if response flag is 'False'"
        except AssertionError as assert_e:
            raise assert_e
        except Exception as err:
            raise AssertionError(f"get_command should not raise errors: {err}")
