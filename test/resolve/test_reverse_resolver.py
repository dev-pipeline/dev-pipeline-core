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


def _get_component_order(config, components):
    order = []

    def _append(resolved_components):
        order.extend(resolved_components)

    devpipeline_core.resolve._process_reverse(components, config, _append)
    return order


class TestReverseResolver(unittest.TestCase):
    def test_linear_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends": "a"}, "c": {"depends": "b"}}
        )
        order = _get_component_order(configuration, ["a"])
        _test_order(self, ["a", "b", "c"], order)

    def test_no_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends": "a"}, "c": {"depends": "b"}}
        )
        order = _get_component_order(configuration, ["c"])
        self.assertEqual(1, len(order))
        self.assertEqual(order[0], "c")


if __name__ == "__main__":
    unittest.main()
