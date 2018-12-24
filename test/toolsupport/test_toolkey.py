#!/usr/bin/python3

import unittest

import devpipeline_core.configinfo
import devpipeline_core.executor
import devpipeline_core.toolsupport


class _MockExecutor(devpipeline_core.executor._ExecutorBase):
    def __init__(self):
        self._warning_count = 0
        self._error_count = 0

    def error(self, msg):
        self._error_count += 1

    def warning(self, msg):
        self._warning_count += 1


class TestToolChooser(unittest.TestCase):
    def test_default_key(self):
        configinfo = devpipeline_core.configinfo.ConfigInfo(_MockExecutor())
        configinfo.config = {"foo": "bar"}
        found_key = devpipeline_core.toolsupport.choose_tool_key(configinfo, ["foo"])
        self.assertEqual("foo", found_key)

    def test_missing_key(self):
        configinfo = devpipeline_core.configinfo.ConfigInfo(_MockExecutor())
        configinfo.config = {"foo": "bar"}
        found_key = devpipeline_core.toolsupport.choose_tool_key(configinfo, ["foo2"])
        self.assertEqual("foo2", found_key)

    def test_nondefault_key(self):
        executor = _MockExecutor()
        configinfo = devpipeline_core.configinfo.ConfigInfo(executor)
        configinfo.config = {"foo": "bar"}
        found_key = devpipeline_core.toolsupport.choose_tool_key(
            configinfo, ["foo2", "foo"]
        )
        self.assertEqual("foo", found_key)
        self.assertEqual(1, executor._warning_count)


if __name__ == "__main__":
    unittest.main()
