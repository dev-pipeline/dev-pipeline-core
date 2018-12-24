#!/usr/bin/python3

import os.path
import sys
import unittest

import devpipeline_core.configinfo
import devpipeline_core.toolsupport

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))

import mockconfig


class _MockExecutor(devpipeline_core.executor._ExecutorBase):
    def __init__(self):
        self._warning_count = 0
        self._error_count = 0

    def error(self, msg):
        self._error_count += 1

    def warning(self, msg):
        self._warning_count += 1


def _found_args(found_args, value, name):
    found_args[name] = value


def _make_found_args(found_args):
    def _wrapper(value, name):
        return _found_args(found_args, value, name)

    return _wrapper


def _compare(tester, expected, actual):
    tester.assertEqual(len(expected), len(actual))
    for expected_key, expected_value in expected.items():
        tester.assertTrue(expected_key in actual)
        tester.assertEqual(expected_value, actual[expected_key])


class TestArgsBuilder(unittest.TestCase):
    def test_tool_no_join(self):
        configuration = mockconfig.MockConfig({"a": {"foo.a": "bar"}})
        config = devpipeline_core.configinfo.ConfigInfo(_MockExecutor())
        config.config = configuration.get("a")
        args = {"a": ""}

        found_args = {}
        devpipeline_core.toolsupport.args_builder(
            "foo", config, args, _make_found_args(found_args)
        )
        expected = {"a": "bar"}
        _compare(self, expected, found_args)

    def test_tool_simple_join(self):
        configuration = mockconfig.MockConfig({"a": {"foo.a": "bar,baz"}})
        config = devpipeline_core.configinfo.ConfigInfo(_MockExecutor())
        config.config = configuration.get("a")
        args = {"a": ""}

        found_args = {}
        devpipeline_core.toolsupport.args_builder(
            "foo", config, args, _make_found_args(found_args)
        )
        expected = {"a": "barbaz"}
        _compare(self, expected, found_args)

    def test_tool_null_join(self):
        configuration = mockconfig.MockConfig({"a": {"foo.a": "bar"}})
        config = devpipeline_core.configinfo.ConfigInfo(_MockExecutor())
        config.config = configuration.get("a")
        args = {"a": None}

        found_args = {}
        devpipeline_core.toolsupport.args_builder(
            "foo", config, args, _make_found_args(found_args)
        )
        expected = {"a": "bar"}
        _compare(self, expected, found_args)

    def test_tool_bad_join(self):
        configuration = mockconfig.MockConfig({"a": {"foo.a": "bar,baz"}})
        config = devpipeline_core.configinfo.ConfigInfo(_MockExecutor())
        config.config = configuration.get("a")
        args = {"a": None}

        found_args = {}

        def _work():
            devpipeline_core.toolsupport.args_builder(
                "foo", config, args, _make_found_args(found_args)
            )

        self.assertRaises(Exception, _work)


if __name__ == "__main__":
    unittest.main()
