#!/usr/bin/python3

import copy


class _TaskQueue:
    def __init__(self, dependencies, reverse_dependencies):
        self._dependencies = copy.deepcopy(dependencies)
        self._reverse_dependencies = copy.deepcopy(reverse_dependencies)

    def __iter__(self):
        while self._dependencies:
            next_tasks = []

            for component, dependencies in self._dependencies.items():
                if not dependencies:
                    next_tasks.append(component)

            if next_tasks:
                yield next_tasks
            else:
                raise Exception("Resolve failure")

    def resolve(self, task):
        del self._dependencies[task]
        for reverse in self._reverse_dependencies[task]:
            del self._dependencies[reverse][task]


class DependencyManager:
    def __init__(self, tasks):
        self._tasks = tasks.copy()
        self._dependencies = {}
        self._reverse_dependencies = {}

    def _validate_implicit_dependencies(self, component):
        task_tuple = (component, self._tasks[0])
        if task_tuple not in self._dependencies:
            last_task = None
            for task in self._tasks:
                task_tuple = (component, task)
                if last_task:
                    last_task_tuple = (component, last_task)
                    self._dependencies[task_tuple] = {last_task_tuple: None}
                    self._reverse_dependencies[last_task_tuple] = {task_tuple: None}
                else:
                    self._dependencies[task_tuple] = {}
                self._reverse_dependencies[task_tuple] = {}
                last_task = task

    def add_dependency(self, component_task, dependent_task):
        def _helper(key, value, table):
            table[key][value] = None

        self._validate_implicit_dependencies(component_task[0])
        if dependent_task:
            self._validate_implicit_dependencies(dependent_task[0])
            _helper(component_task, dependent_task, self._dependencies)
            _helper(dependent_task, component_task, self._reverse_dependencies)

    def get_queue(self):
        return _TaskQueue(self._dependencies, self._reverse_dependencies)
