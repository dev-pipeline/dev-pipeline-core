#!/usr/bin/python3

import copy


class _TaskQueue:
    def __init__(self, dependencies, reverse_dependencies):
        self._dependencies = copy.deepcopy(dependencies)
        self._reverse_dependencies = copy.deepcopy(reverse_dependencies)

    def _get_ready_tasks(self):
        next_tasks = []
        for component, dependencies in self._dependencies.items():
            if not dependencies:
                next_tasks.append(component)
        return next_tasks

    def __iter__(self):
        while self._dependencies:
            next_tasks = self._get_ready_tasks()
            if next_tasks:
                yield next_tasks
            else:
                raise Exception("Resolve failure")

    def resolve(self, task):
        del self._dependencies[task]
        for reverse in self._reverse_dependencies[task]:
            del self._dependencies[reverse][task]

    def fail(self, task):
        local_skipped = []
        for dep in self._dependencies[task]:
            del self._reverse_dependencies[dep][task]
        for reverse in self._reverse_dependencies[task]:
            local_skipped.append(reverse)
        skipped = []
        for skipped_task in local_skipped:
            skipped.append(skipped_task)
            skipped.extend(self.fail(skipped_task))
        del self._dependencies[task]
        return skipped


def _add_implicit(last_task, task_tuple, dependencies, reverse_dependencies):
    if last_task:
        last_task_tuple = (task_tuple[0], last_task)
        dependencies[task_tuple] = {last_task_tuple: None}
        if last_task_tuple not in reverse_dependencies:
            reverse_dependencies[last_task_tuple] = {task_tuple: None}
        else:
            reverse_dependencies[last_task_tuple][task_tuple] = None
    else:
        dependencies[task_tuple] = {}
    reverse_dependencies[task_tuple] = {}


def _fill_implicit(component_task, task_list, dependencies, reverse_dependencies):
    last_task = None
    task_index = task_list.index(component_task[1]) + 1
    for task in task_list[0:task_index]:
        task_tuple = (component_task[0], task)
        if task_tuple not in dependencies:
            _add_implicit(last_task, task_tuple, dependencies, reverse_dependencies)
        last_task = task


class DependencyManager:
    def __init__(self, tasks):
        self._tasks = tasks.copy()
        self._dependencies = {}
        self._reverse_dependencies = {}

    def _validate_implicit_dependencies(self, component_task):
        if component_task not in self._dependencies:
            _fill_implicit(
                component_task,
                self._tasks,
                self._dependencies,
                self._reverse_dependencies,
            )

    def get_dependencies(self, component_task):
        return self._dependencies.get(component_task).keys()

    def get_reverse_dependencies(self, component_task):
        return self._reverse_dependencies.get(component_task).keys()

    def add_dependency(self, component_task, dependent_task):
        def _helper(key, value, table):
            table[key][value] = None

        self._validate_implicit_dependencies(component_task)
        if dependent_task:
            self._validate_implicit_dependencies(dependent_task)
            _helper(component_task, dependent_task, self._dependencies)
            _helper(dependent_task, component_task, self._reverse_dependencies)

    def get_queue(self):
        return _TaskQueue(self._dependencies, self._reverse_dependencies)
