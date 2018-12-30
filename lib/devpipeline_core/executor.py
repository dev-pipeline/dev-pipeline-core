#!/usr/bin/python3

"""
This modules includes various executor classes.  These can be used by Command,
or as templates to implement new executor classes.
"""

import os
import subprocess


def _execute_single(environment, **kwargs):
    # pylint: disable=broad-except
    try:
        subprocess.check_call(env=environment, **kwargs)
    except Exception as failure:
        raise failure


class _ExecutorBase:
    def message(self, msg):
        # pylint: disable=no-self-use
        """
        Display a message to the user.

        Arguments
        msg - the message to display
        """
        print(msg)

    def error(self, msg):
        # pylint: disable=no-self-use
        """
        Display an error message to the user.

        An error means a critical failure has occurred and the tool that raised
        it cannot recover.  In most cases, errors mean termination will cease.

        Arguments
        msg - the error message
        """
        print("ERROR: {}".format(msg))

    def warning(self, msg):
        # pylint: disable=no-self-use
        """
        Display an warning message to the user.

        Warnings are used to convey problems that occurred, but don't represent
        a critical failure.  In most cases, warnings won't prevent regular
        execution.

        Arguments
        msg - the warning message
        """
        print("WARNING: {}".format(msg))

    def execute(self, environment, *args):
        # pylint: disable=no-self-use
        """
        Execute a series of commands.

        Arguments:
        environment - a dictionary-like object containing the environment
                      commands should be executed in
        args - A list of dictionaries to pass to subprocess calls.
        """
        for cmd in args:
            _execute_single(environment, **cmd)


class QuietExecutor(_ExecutorBase):

    """This executor class runs logging minimal information."""

    def message(self, msg):
        pass


_QUIET_EXECUTOR = (
    QuietExecutor,
    "An executor that prints no additional information.  Information pinted by"
    " any executed tools will be printed without modification.",
)


class SilentExecutor(_ExecutorBase):

    """This executor class runs and logs nothing except errors."""

    def message(self, msg):
        pass

    def execute(self, environment, *args):
        # pylint: disable=invalid-name
        with open(os.devnull, "w") as FNULL:
            for cmd in args:
                cmd["stdout"] = FNULL
                _execute_single(environment, **cmd)


_SILENT_EXECUTOR = (
    SilentExecutor,
    "An executor that removes all standard output.  Anything printed to "
    "standard error will still be emitted.",
)


class VerboseExecutor(_ExecutorBase):

    """This executor class logs verbosely."""

    def execute(self, environment, *args):
        for cmd in args:
            cmd_args = cmd.get("args")
            self.message("\tExecuting: {}".format(cmd_args))
            _execute_single(environment, **cmd)


_VERBOSE_EXECUTOR = (
    VerboseExecutor,
    "An executor that prints lots of extra information.",
)


class DryRunExecutor(_ExecutorBase):

    """
    This executor class outputs the commands that would have been run but
    doesn't execute them.
    """

    def execute(self, environment, *args):
        for cmd in args:
            cmd_args = cmd.get("args")
            self.message("\tExecuting: {}".format(cmd_args))


_DRYRUN_EXECUTOR = (
    DryRunExecutor,
    "An executor that prints what it would do, but doesn't execute anthing.  "
    "This is useful for debugging a configuration.",
)
