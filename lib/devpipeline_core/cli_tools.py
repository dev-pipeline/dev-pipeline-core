#!/usr/bin/python3

import devpipeline_core
import devpipeline_core.command
import devpipeline_core.version


def _configure(parser):
    devpipeline_core.command.add_version_info(parser, devpipeline_core.version.STRING)


def _print_resolvers(arguments):
    del arguments

    for dependency_resolver in sorted(devpipeline_core.DEPENDENCY_RESOLVERS):
        print(
            "{} - {}".format(
                dependency_resolver,
                devpipeline_core.DEPENDENCY_RESOLVERS[dependency_resolver][1],
            )
        )


def _print_executors(arguments):
    del arguments

    for executor in sorted(devpipeline_core.EXECUTOR_TYPES):
        print("{} - {}".format(executor, devpipeline_core.EXECUTOR_TYPES[executor][1]))


_RESOLVERS_COMMAND = (
    "List the available resolvers.",
    _configure,
    _print_resolvers,
)


_EXECUTORS_COMMAND = (
    "List the available executors.",
    _configure,
    _print_executors,
)
