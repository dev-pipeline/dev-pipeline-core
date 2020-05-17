#!/usr/bin/python3

"""
Classes and functions releated to executing commands.
"""

import argparse

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


def setup_target_parser(parser):
    parser.add_argument(
        "targets",
        nargs="*",
        default=argparse.SUPPRESS,
        help="The targets to operate on",
    )


def setup_task_parser(parser):
    setup_target_parser(parser)
    parser.add_argument(
        "--dependencies",
        help="Control how build dependencies are handled.",
        default="deep",
    )
    parser.add_argument(
        "--executor", help="The method to execute commands.", default="quiet"
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="If a task fails, continue executing as many remaining tasks as possible.",
    )


def add_version_info(argparser, version):
    argparser.add_argument(
        "--version", action="version", version="%(prog)s {}".format(version)
    )
    return argparser


def _setup_targets(parsed_args, components):
    if "targets" in parsed_args:
        return parsed_args.targets
    parsed_args.dependencies = "deep"
    return components.keys()


def process_targets(arguments, work_fn, config_fn):
    full_config = config_fn()
    targets = _setup_targets(arguments, full_config)
    work_fn(targets, full_config)


def _execute_targets(task_dict, task_queue, config_info, full_config, fail_function):
    for component_tasks in task_queue:
        for component_task in component_tasks:
            task_heading = "  {} ({})".format(component_task[0], component_task[1])
            config_info.executor.message(task_heading)
            config_info.executor.message("-" * (2 + len(task_heading)))

            config_info.config = full_config.get(component_task[0])
            config_info.env = devpipeline_core.env.create_environment(
                config_info.config
            )
            try:
                task_dict[component_task[1]](config_info)
                task_queue.resolve(component_task)
            except Exception as failure:  # pylint: disable=broad-except
                fail_function(failure, component_task)
            config_info.executor.message("")


class _PartialFailureException(Exception):
    def __init__(self, failed):
        self.failed = failed


def process_tasks(arguments, tasks, config_fn):
    def _work_fn(targets, full_config):
        task_order = []
        task_dict = {}
        for name, fn in tasks:
            task_order.append(name)
            task_dict[name] = fn

        executor = _get_executor(arguments)
        resolver = _get_resolver(arguments)
        dep_manager = resolver(targets, full_config, task_order)
        task_queue = dep_manager.get_queue()
        config_info = devpipeline_core.configinfo.ConfigInfo(executor)

        try:
            failed = []

            def _keep_going_on_failure(failure, task):
                skipped = task_queue.fail(task)
                failed.append((task, skipped, str(failure)))

            def _fail_immediately(failure, task):
                del task
                raise failure

            fail_fn = _fail_immediately
            if arguments.keep_going:
                fail_fn = _keep_going_on_failure

            _execute_targets(task_dict, task_queue, config_info, full_config, fail_fn)
            if failed:
                raise _PartialFailureException(failed)
        finally:
            full_config.write()

    process_targets(arguments, _work_fn, config_fn)


def _get_executor(parsed_args):
    helper_fn = devpipeline_core.EXECUTOR_TYPES.get(parsed_args.executor)
    if helper_fn:
        return helper_fn[0]()
    raise Exception("{} isn't a valid executor".format(parsed_args.executor))


def _get_resolver(parsed_args):
    if "dependencies" not in parsed_args:
        parsed_args.dependencies = "deep"
    resolver = devpipeline_core.DEPENDENCY_RESOLVERS.get(parsed_args.dependencies)
    if resolver:
        return resolver[0]
    raise Exception("{} isn't a valid resolver".format(parsed_args.dependencies))
