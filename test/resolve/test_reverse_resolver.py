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


class TestReverseResolver(unittest.TestCase):
    def test_linear_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends.build": "a"}, "c": {"depends.build": "b"}}
        )
        order = _order_resolve(
            devpipeline_core.resolve._process_reverse(["a"], configuration, ["build"])
        )
        _test_order(self, ["a.build", "b.build", "c.build"], order)

    def test_no_deps(self):
        configuration = mockconfig.MockConfig(
            {"a": {}, "b": {"depends.build": "a"}, "c": {"depends.build": "b"}}
        )
        order = _order_resolve(
            devpipeline_core.resolve._process_reverse(["c"], configuration, ["build"])
        )
        self.assertEqual(1, len(order))
        self.assertEqual(order[0], "c.build")


if __name__ == "__main__":
    unittest.main()
