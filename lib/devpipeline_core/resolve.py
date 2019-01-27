#!/usr/bin/python3
"""Resolve dependencies into an order build list"""

import devpipeline_core.taskqueue


class CircularDependencyException(Exception):
    """
    An exception that's thrown when dependencies contain a circular dependency.
    """

    def __init__(self, circular_components):
        super().__init__()
        self.components = circular_components

    def __str__(self):
        return "Circular dependency: {}".format(self.components)


class MissingComponentsException(Exception):
    def __init__(self, missing_components):
        super().__init__()
        self.missing_components = missing_components

    def __str__(self):
        return "Missing component configurations: {}".format(self.missing_components)


def _process_none(targets, components, tasks):
    del components

    dm = devpipeline_core.taskqueue.DependencyManager(tasks)
    for target in targets:
        for task in tasks:
            dm.add_dependency((target, task), None)
    return dm


_NONE_RESOLVER = (
    _process_none,
    "Only explicilty specified targets will be considered.",
)


def _build_target_tasks(targets, tasks):
    target_tasks = []
    known_target_tasks = {}
    for target in targets:
        for task in tasks:
            target_task = (target, task)
            target_tasks.append(target_task)
            known_target_tasks[target_task] = None
    return (target_tasks, known_target_tasks)


def _add_component_dependencies(component_task, dependencies, dm):
    component_dependencies = []
    if dependencies:
        for dependency in dependencies:
            dependent_task = (dependency, component_task[1])
            dm.add_dependency(component_task, dependent_task)
            component_dependencies.append(dependent_task)
    else:
        dm.add_dependency(component_task, None)
    return component_dependencies


def _handle_component_dependencies(component, component_task, dm):
    component_dependencies = []
    dm.add_dependency(component_task, None)
    dependencies = component.get_list("depends.{}".format(component_task[1]))
    component_dependencies.extend(
        _add_component_dependencies(component_task, dependencies, dm)
    )
    return component_dependencies


def calculate_dependencies(targets, full_config, tasks):
    dm = devpipeline_core.taskqueue.DependencyManager(tasks)
    to_process, known_targets = _build_target_tasks(targets, tasks)
    missing_components = []
    while to_process:
        target_task = to_process[0]
        component = full_config.get(target_task[0])
        if component:
            component_dependencies = _handle_component_dependencies(
                component, target_task, dm
            )
            for dependency in component_dependencies:
                if dependency not in known_targets:
                    known_targets[dependency] = None
                    to_process.append(dependency)
        else:
            missing_components.append(target_task[0])
        to_process.pop(0)

    if missing_components:
        raise MissingComponentsException(missing_components)
    return dm


_DEEP_RESOLVER = (
    calculate_dependencies,
    "A resolver that includes the entire dependency tree for every target.",
)


def _process_reverse(targets, components, tasks):
    to_process = list(targets)
    known_targets = {target: None for target in targets}
    full_dm = calculate_dependencies(components.keys(), components, tasks)
    dm = devpipeline_core.taskqueue.DependencyManager(tasks)
    while to_process:
        target = to_process[0]
        for task in tasks:
            component_task = (target, task)
            if target in targets:
                dm.add_dependency(component_task, None)
            for reverse_dependent in full_dm.get_reverse_dependencies(component_task):
                dm.add_dependency(reverse_dependent, component_task)
                if reverse_dependent[0] not in known_targets:
                    known_targets[reverse_dependent[0]] = None
                    to_process.append(reverse_dependent[0])
        to_process.pop(0)
    return dm


_REVERSE_RESOLVER = (
    _process_reverse,
    "A resolver that includes targets plus any component that depends on them.",
)
