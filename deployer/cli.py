"""Console script for deployer-fsm."""
import argparse
import pickle
import sys
import uuid

from deployer.deployer import make_script, parse_commands

DEFAULT_CONFIG = {
    "output": "script-out.sh",
    "commands": "curr_commands.pkl",
    "start": None,
    "unattended": False,
    "host": "localhost",
}


def main(*args):
    """Main deployer-fsm execution function."""
    parser = argparse.ArgumentParser(description="deploy with confidence")
    parser.add_argument("--output", "-o", help="output file save location")
    parser.add_argument(
        "--commands", "-c", help="pickled command FSM file location"
    )
    parser.add_argument(
        "--start", "-s", help="start uuid for deployment chain"
    )
    parser.add_argument(
        "--unattended",
        "-u",
        action="store_true",
        help="dont launch repl after known commands finish",
    )
    parser.add_argument("--host", help="SSH host to deploy on")

    args = vars(parser.parse_args(args[1:]))
    config = dict(DEFAULT_CONFIG, **{
        arg: val
        for arg, val in args
        if val is not None
    })

    start = config["start"]
    start = None if start == "None" or start is None else uuid.UUID(start)

    run(start, config)
    return 0


def run(start, config):
    """Wrapper command for making and saving script/pickle data."""
    with open(DEFAULT_CONFIG["output"], "w") as script_file:
        try:
            with open(DEFAULT_CONFIG["commands"], "rb") as pkl:
                commands, start_idx = pickle.load(pkl)
        except IOError:
            commands, start_idx = {}, None

        start = start or start_idx
        commands, start_idx = make_script(commands, start, config)
        script_file.write(parse_commands(commands, start_idx))

        with open(config["commands"], "wb") as pkl:
            pickle.dump((commands, start_idx), pkl)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))  # pragma: no cover
