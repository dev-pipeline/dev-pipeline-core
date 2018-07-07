#!/usr/bin/python3

"""This module defines several base classes that are common for
the dev-pipeline utility"""

import argparse
import errno
import sys

import devpipeline_core.config.config
import devpipeline_core.config.env
import devpipeline_core.resolve
import devpipeline_core.version


class Command(object):

    """This is the base class for tools that can be used by dev-pipeline.

    In subclasses, override the following as needed:
        execute()
        setup()"""

    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            *args, **kwargs)

    def add_argument(self, *args, **kwargs):
        """Subclasses inject additional cli arguments to parse by calling this function"""
        self.parser.add_argument(*args, **kwargs)

    def set_version(self, version):
        self.parser.add_argument("--version", action="version",
                                 version="%(prog)s {}".format(
                                     devpipeline_core.version.STRING))

    def execute(self, *args, **kwargs):
        """Initializes and runs the tool"""
        args = self.parser.parse_args(*args, **kwargs)
        self.setup(args)
        self.process()

    def setup(self, arguments):
        """Subclasses should override this function to perform any pre-execution setup"""
        pass

    def process(self):
        """Subclasses should override this function to do the work of executing the tool"""
        pass


class TargetCommand(Command):

    """A devpipeline tool that executes a list of tasks against a list of targets"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("targets", nargs="*",
                          help="The targets to operate on")
        self.executor = None
        self.components = None
        self.targets = None
        self.verbosity = False
        self.resolver = None

    def enable_dependency_resolution(self):
        self.add_argument("--dependencies",
                          help="Control how build dependencies are handled.",
                          default="deep")

    def enable_executors(self):
        self.add_argument("--executor",
                          help="The method to execute commands.",
                          default="quiet")
        self.verbosity = True

    def set_tasks(self, tasks):
        self.tasks = tasks

    def execute(self, *args, **kwargs):
        parsed_args = self.parser.parse_args(*args, **kwargs)

        self.components = devpipeline_core.config.config.update_cache()
        if parsed_args.targets:
            self.targets = parsed_args.targets
        else:
            parsed_args.dependencies = "deep"
            self.targets = self.components.sections()
        self.setup(parsed_args)
        if self.verbosity:
            helper_fn = devpipeline_core.EXECUTOR_TYPES.get(parsed_args.executor)
            if not helper_fn:
                raise Exception(
                    "{} isn't a valid executor".format(parsed_args.executor))
            else:
                self.executor = helper_fn()
        if "dependencies" not in parsed_args:
            parsed_args.dependencies = "deep"
        self.resolver = devpipeline_core.DEPENDENCY_RESOLVERS.get(parsed_args.dependencies)
        self.process()

    def process(self):
        build_order = []

        def _listify(resolved_components):
            nonlocal build_order

            build_order += resolved_components

        self.resolver(self.targets, self.components, _listify)
        self.process_targets(build_order)

    def process_targets(self, build_order):
        """Calls the tasks with the appropriate options for each of the targets"""
        config_info = {
            "executor": self.executor
        }
        for target in build_order:
            self.executor.message("  {}".format(target))
            self.executor.message("-" * (4 + len(target)))

            config_info["current_target"] = target
            config_info["current_config"] = self.components[target]
            config_info[target] = {}
            config_info["env"] = devpipeline_core.config.env.create_environment(
                config_info)
            for task in self.tasks:
                task(config_info)
            self.executor.message("")


def make_command(tasks, *args, **kwargs):
    command = TargetCommand(*args, **kwargs)
    command.enable_dependency_resolution()
    command.enable_executors()
    command.set_tasks(tasks)
    return command


def execute_command(command, args):
    """
    Runs the provided command with the given args.  Exceptions are propogated
    to the caller.
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

    except Exception as failure:
        print("Error: {}".format(str(failure)), file=sys.stderr)
        sys.exit(1)
