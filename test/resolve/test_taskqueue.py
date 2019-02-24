#!/usr/bin/python3

import unittest

import devpipeline_core.taskqueue


class TestDependencyManager(unittest.TestCase):
    def _resolve_tasks(self, task_queue):
        resolved_tasks = []
        for resolved in task_queue:
            for resolved_task in resolved:
                self.assertFalse(resolved_task in resolved_tasks)
                task_queue.resolve(resolved_task)
            resolved_tasks.extend(resolved)
        return resolved_tasks

    def _resolve_helper(self, dm, components):
        task_queue = dm.get_queue()
        return self._resolve_tasks(task_queue)

    def test_no_deps(self):
        components = ["foo", "bar"]
        tasks = ["checkout"]
        dm = devpipeline_core.taskqueue.DependencyManager(tasks)
        dm.add_dependency((components[0], tasks[0]), None)
        dm.add_dependency((components[1], tasks[0]), None)
        resolved_tasks = self._resolve_helper(dm, components)
        expected_tasks = [("foo", "checkout"), ("bar", "checkout")].sort()
        self.assertEqual(resolved_tasks.sort(), expected_tasks)

    def test_implicit_deps(self):
        components = ["foo"]
        tasks = ["checkout", "build", "test", "install"]
        dm = devpipeline_core.taskqueue.DependencyManager(tasks)
        dm.add_dependency((components[0], tasks[3]), None)
        resolved_tasks = self._resolve_helper(dm, components)
        expected_tasks = [
            ("foo", "checkout"),
            ("foo", "build"),
            ("foo", "test"),
            ("foo", "install"),
        ]
        self.assertEqual(resolved_tasks, expected_tasks)

    def test_partial_implicit_deps(self):
        components = ["foo"]
        tasks = ["checkout", "build", "test", "install"]
        dm = devpipeline_core.taskqueue.DependencyManager(tasks)
        dm.add_dependency((components[0], tasks[1]), None)
        resolved_tasks = self._resolve_helper(dm, components)
        expected_tasks = [("foo", "checkout"), ("foo", "build")]
        self.assertEqual(resolved_tasks, expected_tasks)

    def test_explicit_deps(self):
        components = ["foo", "bar"]
        tasks = ["build"]
        dm = devpipeline_core.taskqueue.DependencyManager(tasks)
        dm.add_dependency(("bar", "build"), ("foo", "build"))
        resolved_tasks = self._resolve_helper(dm, components)
        expected_tasks = [("foo", "build"), ("bar", "build")]
        self.assertEqual(resolved_tasks, expected_tasks)

    def test_fail(self):
        components = ["foo"]
        tasks = ["checkout", "build", "install"]
        dm = devpipeline_core.taskqueue.DependencyManager(tasks)
        dm.add_dependency(("foo", "install"), None)
        task_queue = dm.get_queue()
        skipped_tasks = sorted(task_queue.fail(("foo", "checkout")))
        expected_tasks = [("foo", "build"), ("foo", "install")]
        self.assertEqual(skipped_tasks, expected_tasks)

    def test_fail_some(self):
        components = ["foo", "bar"]
        tasks = ["checkout", "build"]
        dm = devpipeline_core.taskqueue.DependencyManager(tasks)
        dm.add_dependency(("foo", "build"), None)
        dm.add_dependency(("bar", "build"), None)
        dm.add_dependency(("bar", "build"), ("foo", "build"))
        task_queue = dm.get_queue()
        skipped_tasks = task_queue.fail(("foo", "build"))
        resolved_tasks = self._resolve_tasks(task_queue)
        expected_complete = [("foo", "checkout"), ("bar", "checkout")]
        expected_skipped = [("bar", "build")]
        self.assertEqual(resolved_tasks, expected_complete)
        self.assertEqual(skipped_tasks, expected_skipped)


if __name__ == "__main__":
    unittest.main()
