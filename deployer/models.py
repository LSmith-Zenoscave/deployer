"""deployer data models."""


class Command:
    """A basic command to be run by the deployer."""
    def __init__(self, command, desc, cmd_id, state=None):
        self.command = command
        self.desc = desc
        self.cmd_id = cmd_id
        self.state = state or dict()

    def __repr__(self):
        return (
            f"Command("
            f"command={repr(self.command)}, "
            f"desc={repr(self.desc)}, "
            f"id={repr(self.cmd_id)}, "
            f"state={repr(self.state)})"
        )

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return hash(self.cmd_id)

    def __eq__(self, value):
        return (
            self.__class__ == value.__class__ and
            hash(self) == hash(value)
        )
