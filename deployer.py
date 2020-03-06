import pickle
import uuid
from fabric import Connection
from invoke import UnexpectedExit

def main():
    with open('script-out.sh', 'w') as script_file:
        try:
            with open("curr_commands.pkl", "rb") as pkl:
                commands, start_idx = pickle.load(pkl)
        except IOError:
            commands, start_idx = {}, None

        commands, start_idx = make_script(commands, start_idx)
        script_file.write(parseCommands(commands, start_idx))

        with open("curr_commands.pkl", "wb") as pkl:
            pickle.dump((commands, start_idx), pkl)

def make_script(commands, start_idx):
    prev_exit = 0
    prev_command = None
    curr_idx = start_idx
    while curr_idx is not None and curr_idx in commands:
        next_command = commands[curr_idx]
        print(f"Running: {next_command['desc']}")
        try: 
            result = Connection('localhost').run(next_command["command"], pty=True, warn=False)
        except UnexpectedExit as ex: 
            result = ex.result
        prev_command = next_command
        prev_exit = result.exited
        if result.exited in next_command:
            curr_idx = next_command[result.exited]
        else:
            curr_idx = None

    while True:
        command, keep_going = getCommand()
        if not keep_going:
            break
        try:
            result = Connection('localhost').run(command["command"], pty=True, warn=False)
        except UnexpectedExit as ex:
            result = ex.result
        commands, prev_exit = updateCommands(commands, prev_command, prev_exit, command, result)
        prev_command = command
        if start_idx is None:
            start_idx = command["id"]

    return commands, start_idx

def getCommand():
    command_lines = []
    if query_yes_no("Enter another command?", default="yes"):
        desc = input("Enter one-line description of command: ")
        print("Enter/Paste your command. Ctrl-D (Ctrl-Z on windows) to finish.")
        while True:
            try:
                line = input("> ")
            except EOFError:
                print()
                break
            command_lines.append(line)
        command = "\n".join(command_lines)
        return {"command": command, "id": uuid.uuid4(), "desc": desc}, True
    return None, False


def query_yes_no(prompt, default=None):
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
        elif choice in valid:
            return choice in yes_resp
        else:
            print("Please respond with 'yes'(y) or 'no'(n).")


def updateCommands(commands, prev_command, prev_exit, command, result):
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

def parseCommands(commands, start_id):
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
        func = func_template.format(idx=idx, desc=desc, command=command, results=results)
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

if __name__ == '__main__':
    main()
