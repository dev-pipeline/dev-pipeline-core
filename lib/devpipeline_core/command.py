#!/usr/bin/python3

"""
Classes and functions releated to executing commands.
"""

import argparse
import errno
import sys

import devpipeline_core.configinfo
import devpipeline_core.env
import devpipeline_core.resolve
import devpipeline_core.version


def _print_resolvers():
    for dependency_resolver in sorted(devpipeline_core.DEPENDENCY_RESOLVERS):
        print(
            "{} - {}".format(
                dependency_resolver,
                devpipeline_core.DEPENDENCY_RESOLVERS[dependency_resolver][1],
            )
        )


def _print_executors():
    for executor in sorted(devpipeline_core.EXECUTOR_TYPES):
        print("{} - {}".format(executor, devpipeline_core.EXECUTOR_TYPES[executor][1]))


class Command(object):

    """This is the base class for dev-pipeline commands.

    In subclasses, override the following as needed:
        execute()
        setup()
    """

    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter, *args, **kwargs
        )

    def add_argument(self, *args, **kwargs):
        """
        Subclasses inject additional cli arguments to parse by calling this
        function.  Arguments are passed to an argparse.ArgumentParser instance.
        """
        self.parser.add_argument(*args, **kwargs)

    def set_version(self, version):
        """
        Add the --version string with appropriate output.

        Arguments:
        version - the version of whatever provides the command
        """
        self.parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s {} (core {})".format(
                version, devpipeline_core.version.STRING
            ),
        )

    def execute(self, *args, **kwargs):
        """
        Initializes and runs the tool.

        This is shorhand to parse command line arguments, then calling:
            self.setup(parsed_arguments)
            self.process()
        """
        args = self.parser.parse_args(*args, **kwargs)
        self.setup(args)
        self.process()

    def setup(self, arguments):
        """
        Configure the command.  Subclasses should override this function if
        they need to change behavior based on the command line arguments.

        Arguments:
        arguments - result of argparse.ArgumentParser.parse_args
        """
        pass

    def process(self):
        """
        Execute the command.  Subclasses are expected to override this
        function.
        """
        pass


def _setup_targets(parsed_args, components):
    if "targets" in parsed_args:
        return parsed_args.targets
    parsed_args.dependencies = "deep"
    return components.keys()


class TargetCommand(Command):

    """
    A devpipeline command that operates against a list of targets.
    """

    def __init__(self, config_fn, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument(
            "targets",
            nargs="*",
            default=argparse.SUPPRESS,
            help="The targets to operate on",
        )
        self.components = None
        self.targets = None
        self._config_fn = config_fn

    def execute(self, *args, **kwargs):
        parsed_args = self.parser.parse_args(*args, **kwargs)
        self.components = self._config_fn()
        self.targets = _setup_targets(parsed_args, self.components)
        self.setup(parsed_args)
        self.process()


def _get_executor(parsed_args):
    helper_fn = devpipeline_core.EXECUTOR_TYPES.get(parsed_args.executor)
    if helper_fn:
        return helper_fn[0]()
    else:
        raise Exception("{} isn't a valid executor".format(parsed_args.executor))


def _get_resolver(parsed_args):
    if "dependencies" not in parsed_args:
        parsed_args.dependencies = "deep"
    resolver = devpipeline_core.DEPENDENCY_RESOLVERS.get(parsed_args.dependencies)
    if resolver:
        return resolver[0]
    else:
        raise Exception("{} isn't a valid resolver".format(parsed_args.dependencies))


class TaskCommand(TargetCommand):
    """
    A devpipeline command that executes a list of tasks against a list of
    targets.
    """

    def __init__(self, config_fn, tasks, *args, **kwargs):
        super().__init__(config_fn=config_fn, *args, **kwargs)
        self._tasks = tasks
        self._special_options = {}

        # Dependency resolution
        self.add_argument(
            "--dependencies",
            help="Control how build dependencies are handled.",
            default="deep",
        )
        self.add_argument(
            "--list-dependency-resolvers",
            action="store_true",
            default=argparse.SUPPRESS,
            help="List the dependency resolution methods.",
        )
        self._special_options["list_dependency_resolvers"] = _print_resolvers

        # Executor stuff
        self.add_argument(
            "--executor", help="The method to execute commands.", default="quiet"
        )
        self.add_argument(
            "--list-executors",
            action="store_true",
            default=argparse.SUPPRESS,
            help="List the available executors.",
        )
        self.verbosity = True
        self._special_options["list_executors"] = _print_executors

    def execute(self, *args, **kwargs):
        parsed_args = self.parser.parse_args(*args, **kwargs)

        def _check_special_options():
            for option, option_fn in self._special_options.items():
                if option in parsed_args:
                    return option_fn
            return None

        special_fn = _check_special_options()
        if special_fn:
            return special_fn()
        self.components = self._config_fn()
        self.targets = _setup_targets(parsed_args, self.components)
        self.setup(parsed_args)
        executor = _get_executor(parsed_args)
        resolver = _get_resolver(parsed_args)
        return self.process_targets(resolver, executor)

    def process_targets(self, resolver, executor):
        """
        Calls the tasks with the appropriate options for each of the targets.
        """
        build_order = []

        def _listify(resolved_components):
            nonlocal build_order

            build_order += resolved_components

        resolver(self.targets, self.components, _listify)
        config_info = devpipeline_core.configinfo.ConfigInfo(executor)

        try:
            for target in build_order:
                config_info.executor.message("  {}".format(target))
                config_info.executor.message("-" * (4 + len(target)))

                config_info.config = self.components.get(target)
                config_info.env = devpipeline_core.env.create_environment(
                    config_info.config
                )
                for task in self._tasks:
                    task(config_info)
                executor.message("")
        finally:
            self.components.write()


def make_command(tasks, *args, **kwargs):
    """
    Create a TaskCommand with defined tasks.

    This is a helper function to avoid boiletplate when dealing with simple
    cases (e.g., all cli arguments can be handled by TaskCommand), with no
    special processing.  In general, this means a command only needs to run
    established tasks.

    Arguments:
    tasks - the tasks to execute
    args - extra arguments to pass to the TargetCommand constructor
    kwargs - extra keyword arguments to pass to the TargetCommand constructor
    """
    command = TaskCommand(tasks=tasks, *args, **kwargs)
    return command


def execute_command(command, args):
    """
    Runs the provided command with the given args.

    Exceptions, if any, are propogated to the caller.

    Arguments:
    command - something that extends the Command class
    args - A list of command line arguments.  If args is None, sys.argv
           (without the first argument--assumed to be the command name) will
           be used.
    """
    if args is None:
        args = sys.argv[1:]
    try:
        command.execute(args)

    except IOError as failure:
        if failure.errno == errno.EPIPE:
            # This probably means we were piped into something that terminated
            # (e.g., head).  Might be a better way to handle this, but for now
            # silently swallowing the error isn't terrible.
            pass

    except Exception as failure:  # pylint: disable=broad-except
        print("Error: {}".format(str(failure)), file=sys.stderr)
        sys.exit(1)
