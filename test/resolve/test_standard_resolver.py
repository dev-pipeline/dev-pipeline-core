#!/usr/bin/python3

import os.path
import sys
import unittest

import devpipeline_core.resolve

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))

import mockconfig


def _test_order(tester, expected_order, dependant_order):
    last_index = -1
    for component in expected_order:
        new_index = dependant_order.index(component)
        tester.assertLess(last_index, new_index)
        last_index = new_index


class TestStandardResolver(unittest.TestCase):
    def test_single(self):
        configuration = mockconfig.MockConfig({"foo": {}})
        order = devpipeline_core.resolve.order_dependencies(["foo"], configuration)
        self.assertEqual(1, len(order))
        self.assertEqual(order[0], "foo")

    def test_single_target(self):
        configuration = mockconfig.MockConfig({"foo": {}, "bar": {}})
        order = devpipeline_core.resolve.order_dependencies(["foo"], configuration)
        self.assertEqual(1, len(order))
        self.assertEqual(order[0], "foo")

    def test_multiple(self):
        configuration = mockconfig.MockConfig({"foo": {}, "bar": {}})
        order = devpipeline_core.resolve.order_dependencies(
            ["foo", "bar"], configuration
        )
        self.assertEqual(2, len(order))
        self.assertTrue("foo" in order)
        self.assertTrue("bar" in order)

    def test_linear_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends": "a"}, "c": {"depends": "b"}}
        )
        order = devpipeline_core.resolve.order_dependencies(["c"], configuration)
        _test_order(self, ["a", "b", "c"], order)

    def test_common_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends": "a"}, "c": {"depends": "a"}}
        )
        order = devpipeline_core.resolve.order_dependencies(["b", "c"], configuration)
        _test_order(self, ["a", "b"], order)
        _test_order(self, ["a", "c"], order)

    def test_multi_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends": "a"}, "c": {"depends": "a, b"}}
        )
        order = devpipeline_core.resolve.order_dependencies(["c"], configuration)
        _test_order(self, ["a", "b", "c"], order)

    def test_circular_deps(self):
        configuration = mockconfig.MockConfig({"b": {"depends": "b"}})

        def _run_fn():
            order = devpipeline_core.resolve.order_dependencies(["b"], configuration)

        self.assertRaises(devpipeline_core.resolve.CircularDependencyException, _run_fn)


if __name__ == "__main__":
    unittest.main()
