"""Unit tests for deployer.cli module"""
# pylint: disable=too-few-public-methods,too-many-arguments
from deployer import cli
TEST_SCRIPT = __file__


class TestMain:
    """Unit test scenarios for deployer.cli.main"""

    scenarios = {
        "no_args": {
            "user_args": [],
            "result_config": cli.DEFAULT_CONFIG
        },
        "unattended": {
            "user_args": ["--unattended"],
            "result_config": dict(cli.DEFAULT_CONFIG, unattended=True)
        }
    }

    @staticmethod
    def test_main(mocker, user_args, result_config):
        """when main is called it:
        * should not raise errors
        * should parse all args into a config to reflect user choices
        * should call deployer.cli.run
        """
        run_mocked = mocker.patch('deployer.cli.run')
        try:
            cli.main(*[TEST_SCRIPT]+user_args)
            run_mocked.assert_called_with(None, result_config)
        except AssertionError as assert_err:
            raise assert_err
        except Exception as err:
            raise AssertionError(f"main should not raise errors: {err}")


def test_run(mocker):
    """Unit test scenarios for deployer.cli.run:
        when run is called it:
        * should not raise errors
        * should load pickled commands, if they exist
        * should call deployer.deployer.make_script
        * should call deployer.deployer.parse_commands
    """
    config = dict(cli.DEFAULT_CONFIG, commands='test_string_43')
    command_set = ['commands']
    start_idx = 47

    make_script_mock = mocker.patch('deployer.cli.make_script')
    make_script_mock.return_value = (None, None)

    parser_mock = mocker.patch('deployer.cli.parse_commands')

    open_mock = mocker.patch(
        'builtins.open',
        mocker.mock_open(read_data='should never read this')
    )

    pickle_mock = mocker.patch('pickle.load')
    pickle_mock.return_value = (command_set, start_idx)

    try:
        cli.run(None, config)
        assert open_mock.call_count > 0
        assert pickle_mock.call_count == 1
        assert make_script_mock.call_count == 1
        assert parser_mock.call_count == 1

    except AssertionError as assert_err:
        raise assert_err
    except Exception as err:
        raise AssertionError(f"main should not raise errors: {err}")
