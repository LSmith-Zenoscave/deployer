"""FSM and REPL functinality for deployer-fsm."""
import uuid

from fabric import Connection
from invoke import UnexpectedExit


def make_script(commands, start_idx, config):
    """Script run/create entry point."""
    prev_exit = 0
    prev_command = None
    curr_idx = start_idx
    while curr_idx is not None and curr_idx in commands:
        next_command = commands[curr_idx]
        print(f"Running: {next_command['desc']}")
        try:
            result = Connection(config['host']).run(
                next_command["command"], pty=True, warn=False)
        except UnexpectedExit as ex:
            result = ex.result
        prev_command = next_command
        prev_exit = result.exited
        if result.exited in next_command:
            curr_idx = next_command[result.exited]
        else:
            break

    if config['unattended']:
        print("The script finished with exit code", prev_exit)
        if prev_exit != 0:
            print(f"""
Warning!!! The script did not succeed (possibly)
If that is the case, you have a few options
1. Run the failed command manually and resume the unnattended deployment:
i.e.
$ {next_command["command"]}
$ deployer-fsm -u -s '{next_command.get(0, None)}'

2. Rerun from the same starting point as the failed command:
$ deployer-fsm -u -s '{curr_idx}'

3. Do either of the above but with repl feed back (remove the -u flag).
$ {next_command["command"]}
$ deployer-fsm -s '{next_command.get(0, None)}'
~or~
$ deployer-fsm -s '{curr_idx}'

""")
        return commands, start_idx

    while True:
        command, keep_going = get_command()
        if not keep_going:
            break
        try:
            result = Connection('localhost').run(
                command["command"], pty=True, warn=False)
        except UnexpectedExit as ex:
            result = ex.result
        commands, prev_exit = update_commands(
            commands, prev_command, prev_exit, command, result)
        prev_command = command
        if start_idx is None:
            start_idx = command["id"]

    return commands, start_idx


def get_command():
    """gets a bash command as a string from a small user repl."""
    command_lines = []
    if query_yes_no("Enter another command?", default="yes"):
        desc = input("Enter one-line description of command: ")
        print("Enter/Paste your command. Ctrl-D (Ctrl-Z on windows) to finish")
        while True:
            try:
                line = input("> ")
            except (StopIteration, EOFError):
                print()
                break
            command_lines.append(line)
        command = "\n".join(command_lines)
        return {"command": command, "id": uuid.uuid4(), "desc": desc}, True
    return None, False


def query_yes_no(prompt, default=None):
    """CLI [y/n] prompt with configurable default.
    comparable to apt's prompt for yes/no
    """
    yes_resp = ["yes", "y", "ye"]
    no_resp = ["no", "n"]

    valid = yes_resp + no_resp

    if default is None:
        prompt += " [y/n] "
    elif default in yes_resp:
        prompt += " [Y/n] "
    elif default in no_resp:
        prompt += " [y/N] "
    else:
        raise ValueError(f"invalid default answer: {default}")

    while True:
        choice = input(prompt).lower()
        if default is not None and choice == '':
            return default in yes_resp
        if choice in valid:
            return choice in yes_resp
        print("Please respond with 'yes'(y) or 'no'(n).")


def update_commands(commands, prev_command, prev_exit, command, result):
    """Edits the FSM for commands.
    Bases new connection on previous state, edge and current state.
    """
    if result.exited != 0:
        print(f"The last command failed (exit code = {result.exited})...")
        if query_yes_no("Discard command and halt?", default="yes"):
            return commands, result.exited

    if prev_command is not None and "id" in prev_command:
        prev_command = commands.get(prev_command["id"], prev_command)
        prev_command[prev_exit] = command["id"]
        commands[prev_command["id"]] = prev_command

    commands[command["id"]] = command
    return commands, result.exited


def parse_commands(commands, start_id):
    """Command FSM to bash script generator."""
    func_template = """
function command_{idx}() {{

    echo '{desc}'
    {command}
    exit_code=$?
{results}}}
"""

    result_template = """
    if [[ ${{exit_code}} = {code} ]] ; then
        command_{next_idx} # {next_desc}
    fi
"""

    script = "#!/bin/bash\n"

    meta_info = ["command", "id", "desc"]

    for idx, seq in commands.items():
        command = seq['command'].replace("\n", "\n\t")
        desc = seq["desc"]
        results = "".join(
            result_template.format(
                code=code,
                next_idx=next_idx,
                next_desc=commands[next_idx]["desc"]
            )
            for code, next_idx in seq.items()
            if code not in meta_info and next_idx is not None
        )
        func = func_template.format(
            idx=idx, desc=desc, command=command, results=results)
        script += func

    script += f"""
function command_None() {{
    echo "This script is not finished."
    exit 1
}}

command_{start_id}
echo "Done: ${{exit_code}}"
exit ${{exit_code}}
"""

    return script
