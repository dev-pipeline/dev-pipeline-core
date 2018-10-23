#!/usr/bin/python3

"""Test code related to environment overrides"""

import os.path
import unittest

import devpipeline_core.config.paths
import devpipeline_core.config.env

_CONFIG_DIR = "{}/../files".format(os.path.dirname(os.path.abspath(__file__)))


class _ConfigWrapper:
    def __init__(self, vals):
        self._vals = vals

    def get(self, key, raw=False, fallback=None):
        if key in self._vals:
            return self._vals[key]
        return fallback

    def get_list(self, key, fallback=None, split=','):
        fallback = fallback or []
        ret = self.get(key, fallback)
        if ret:
            return ret.split(split)
        return ret

    def __iter__(self):
        return iter(self._vals)


def _make_config_map(target, profile_list, override_list):
    ret = {
        "config_dir": _CONFIG_DIR,
        "current_target": target,
        "current_config": {},
        target: {}
    }
    config = {}
    if profile_list:
        config["dp.profile_name"] = profile_list
    if override_list:
        config["dp.overrides"] = override_list
    ret["current_config"] = _ConfigWrapper(config)
    return ret


class TestEnvironmentLists(unittest.TestCase):
    """Test various methods of modifying the environment"""

    def _validate_env_list(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for key in expected:
            self.assertTrue(key in actual)

    def test_empty_none(self):
        """Verify nothing hapens when a build has no external configuration"""
        expected = {}
        config_map = _make_config_map("foo", None, None)
        env_list = devpipeline_core.config.env.get_env_list(config_map)
        self._validate_env_list(expected, env_list)

    def test_empty_profile(self):
        """Verify nothing hapens when no profile modifies the environment"""
        expected = {}
        config_map = _make_config_map("foo", "debug", None)
        env_list = devpipeline_core.config.env.get_env_list(config_map)
        self._validate_env_list(expected, env_list)

    def test_profile(self):
        """Verify a single profile can modify the environment"""
        expected = {
            "path": None
        }
        config_map = _make_config_map("foo", "local-path", None)
        env_list = devpipeline_core.config.env.get_env_list(config_map)
        self._validate_env_list(expected, env_list)

    def test_duplicate_profile(self):
        """
        Verify a single entry when multiple profiles both alter that environment
        variable.
        """
        expected = {
            "path": None
        }
        config_map = _make_config_map("foo", "local-path,local-path2", None)
        env_list = devpipeline_core.config.env.get_env_list(config_map)
        self._validate_env_list(expected, env_list)

    def test_multiple_profile(self):
        """
        Verify that a single profile can modify multiple environment variables.
        """
        expected = {
            "bar": None,
            "foo": None
        }
        config_map = _make_config_map("foo", "env-fun", None)
        env_list = devpipeline_core.config.env.get_env_list(config_map)
        self._validate_env_list(expected, env_list)

    def test_override(self):
        """
        Verify that override configurations can alter environment variables.
        """
        expected = {
            "bar": None,
            "baz": None,
            "foo": None
        }
        config_map = _make_config_map("foo", None, "env-multi")
        env_list = devpipeline_core.config.env.get_env_list(config_map)
        self._validate_env_list(expected, env_list)


if __name__ == "__main__":
    unittest.main()
