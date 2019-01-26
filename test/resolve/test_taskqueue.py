#!/usr/bin/python3

import unittest

import devpipeline_core.taskqueue


class TestDependencymanager(unittest.TestCase):
    def _resolve_helper(self, dm, components, tasks):
        resolved_tasks = []
        task_queue = dm.get_queue()
        for resolved in task_queue:
            for resolved_task in resolved:
                self.assertFalse(resolved_task in resolved_tasks)
                task_queue.resolve(resolved_task)
            resolved_tasks.extend(resolved)
        return resolved_tasks

    def test_no_deps(self):
        components = ["foo", "bar"]
        tasks = ["checkout"]
        dm = devpipeline_core.taskqueue.DependencyManager(tasks)
        dm.add_dependency((components[0], tasks[0]), None)
        dm.add_dependency((components[1], tasks[0]), None)
        resolved_tasks = self._resolve_helper(dm, components, tasks)
        expected_tasks = [("foo", "checkout"), ("bar", "checkout")].sort()
        self.assertEqual(resolved_tasks.sort(), expected_tasks)

    def test_implicit_deps(self):
        components = ["foo"]
        tasks = ["checkout", "build", "test", "install"]
        dm = devpipeline_core.taskqueue.DependencyManager(tasks)
        dm.add_dependency((components[0], tasks[0]), None)
        resolved_tasks = self._resolve_helper(dm, components, tasks)
        expected_tasks = [
            ("foo", "checkout"),
            ("foo", "build"),
            ("foo", "test"),
            ("foo", "install"),
        ]
        self.assertEqual(resolved_tasks, expected_tasks)

    def test_explicit_deps(self):
        components = ["foo", "bar"]
        tasks = ["build"]
        dm = devpipeline_core.taskqueue.DependencyManager(tasks)
        dm.add_dependency(("bar", "build"), ("foo", "build"))
        resolved_tasks = self._resolve_helper(dm, components, tasks)
        expected_tasks = [("foo", "build"), ("bar", "build")]
        self.assertEqual(resolved_tasks, expected_tasks)


if __name__ == "__main__":
    unittest.main()
