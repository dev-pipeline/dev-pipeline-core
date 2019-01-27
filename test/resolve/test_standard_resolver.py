#!/usr/bin/python3

import os.path
import sys
import unittest

import devpipeline_core.resolve

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))

import mockconfig


def _order_resolve(dm):
    order = []
    task_queue = dm.get_queue()
    for component_tasks in task_queue:
        for component_task in component_tasks:
            order.append("{}.{}".format(component_task[0], component_task[1]))
            task_queue.resolve(component_task)
    return order


def _test_order(tester, expected_order, dependant_order):
    last_index = -1
    for component in expected_order:
        new_index = dependant_order.index(component)
        tester.assertLess(last_index, new_index)
        last_index = new_index


class TestStandardResolver(unittest.TestCase):
    def test_single(self):
        configuration = mockconfig.MockConfig({"foo": {}})
        order = _order_resolve(
            devpipeline_core.resolve.calculate_dependencies(
                ["foo"], configuration, ["build"]
            )
        )
        self.assertEqual(1, len(order))
        self.assertEqual(order[0], "foo.build")

    def test_single_target(self):
        configuration = mockconfig.MockConfig({"foo": {}, "bar": {}})
        order = _order_resolve(
            devpipeline_core.resolve.calculate_dependencies(
                ["foo"], configuration, ["build"]
            )
        )
        self.assertEqual(1, len(order))
        self.assertEqual(order[0], "foo.build")

    def test_multiple(self):
        configuration = mockconfig.MockConfig({"foo": {}, "bar": {}})
        order = _order_resolve(
            devpipeline_core.resolve.calculate_dependencies(
                ["foo", "bar"], configuration, ["build"]
            )
        )
        self.assertEqual(2, len(order))
        self.assertTrue("foo.build" in order)
        self.assertTrue("bar.build" in order)

    def test_linear_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends.build": "a"}, "c": {"depends.build": "b"}}
        )
        order = _order_resolve(
            devpipeline_core.resolve.calculate_dependencies(
                ["c"], configuration, ["build"]
            )
        )
        _test_order(self, ["a.build", "b.build", "c.build"], order)

    def test_common_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends.build": "a"}, "c": {"depends.build": "a"}}
        )
        order = _order_resolve(
            devpipeline_core.resolve.calculate_dependencies(
                ["b", "c"], configuration, ["build"]
            )
        )
        _test_order(self, ["a.build", "b.build"], order)
        _test_order(self, ["a.build", "c.build"], order)

    def test_multi_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends.build": "a"}, "c": {"depends.build": "a, b"}}
        )
        order = _order_resolve(
            devpipeline_core.resolve.calculate_dependencies(
                ["c"], configuration, ["build"]
            )
        )
        _test_order(self, ["a.build", "b.build", "c.build"], order)

    def test_complex_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends.build": "a"}, "c": {"depends.checkout": "b"}}
        )
        order = _order_resolve(
            devpipeline_core.resolve.calculate_dependencies(
                ["c"], configuration, ["checkout", "build"]
            )
        )
        _test_order(self, ["b.checkout", "c.checkout", "c.build"], order)

    def test_missing_component(self):
        configuration = mockconfig.MockConfig({})

        def _run_fn():
            devpipeline_core.resolve.calculate_dependencies(
                ["foo"], configuration, ["build"]
            )

        self.assertRaises(devpipeline_core.resolve.MissingComponentsException, _run_fn)

    def test_circular_deps(self):
        configuration = mockconfig.MockConfig({"b": {"depends": "b"}})

        def _run_fn():
            devpipeline_core.resolve.calculate_dependencies(
                ["b"], configuration, ["build"]
            )

        self.assertRaises(devpipeline_core.resolve.CircularDependencyException, _run_fn)


if __name__ == "__main__":
    unittest.main()
