#!/usr/bin/python3
"""This modules includes various executor classes which determine how the
build is executed - quiet, dry run, ..."""

import os
import subprocess


class _ExecutorBase:
    # pylint: disable=R0201,missing-docstring

    def message(self, msg):
        print(msg)

    # pylint: disable=R0201,missing-docstring
    def error(self, msg):
        print("ERROR: {}".format(msg))

    # pylint: disable=R0201,missing-docstring
    def warning(self, msg):
        print("WARNING: {}".format(msg))

    def _execute_single(self, environment, **kwargs):
        # pylint: disable=broad-except
        try:
            subprocess.check_call(env=environment, **kwargs)
        except Exception as failure:
            raise failure

    def execute(self, environment, *args):
        for cmd in args:
            self._execute_single(environment, **cmd)


class QuietExecutor(_ExecutorBase):

    """This executor class runs logging minimal information."""

    def message(self, msg):
        pass


_QUIET_EXECUTOR = (
    QuietExecutor,
    "An executor that prints no additional information.  Information pinted by"
    " any executed tools will be printed without modification.")


class SilentExecutor(_ExecutorBase):

    """This executor class runs and logs nothing except errors."""

    def message(self, msg):
        pass

    def execute(self, environment, *args):
        # pylint: disable=invalid-name
        with open(os.devnull, 'w') as FNULL:
            for cmd in args:
                cmd["stdout"] = FNULL
                self._execute_single(environment, **cmd)


_SILENT_EXECUTOR = (
    SilentExecutor,
    "An executor that removes all standard output.  Anything printed to "
    "standard error will still be emitted.")


class VerboseExecutor(_ExecutorBase):

    """This executor class logs verbosely."""

    def execute(self, environment, *args):
        for cmd in args:
            cmd_args = cmd.get("args")
            self.message("\tExecuting: {}".format(cmd_args))
            self._execute_single(environment, **cmd)


_VERBOSE_EXECUTOR = (
    VerboseExecutor,
    "An executor that prints lots of extra information.")


class DryRunExecutor(_ExecutorBase):

    """This executor class outputs the commands that would have been run but
    does not execute them."""

    def execute(self, environment, *args):
        for cmd in args:
            cmd_args = cmd.get("args")
            self.message("\tExecuting: {}".format(cmd_args))


_DRYRUN_EXECUTOR = (
    DryRunExecutor,
    "An executor that prints what it would do, but doesn't execute anthing.  "
    "This is useful for debugging a configuration.")
