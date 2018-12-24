#!/usr/bin/python3

import os.path
import sys
import unittest

import devpipeline_core.toolsupport

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))

import mockconfig

_TOOL_FNS = {"bar": (lambda: None, "bar")}


class TestToolBuilder(unittest.TestCase):
    def test_tool_exists(self):
        config = {"foo": "bar"}
        tool = devpipeline_core.toolsupport.tool_builder(config, "foo", _TOOL_FNS)
        self.assertEqual(None, tool)

    def test_tool_missing(self):
        config = mockconfig.MockComponent("a", {})

        def _build_tool():
            return devpipeline_core.toolsupport.tool_builder(config, "foo", _TOOL_FNS)

        self.assertRaises(devpipeline_core.toolsupport.MissingToolKey, _build_tool)


if __name__ == "__main__":
    unittest.main()
