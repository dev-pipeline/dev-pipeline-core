#!/usr/bin/python3

"""Functions related to configuration paths"""

import os.path

_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".dev-pipeline.d")


def _get_config_dir():
    env_override = os.environ.get("DEV_PIPELINE_CONFIG")
    if env_override:
        return env_override
    return _DEFAULT_PATH


def _make_path(base_dir, *endings):
    if not base_dir:
        base_dir = _get_config_dir()
    return os.path.join(base_dir, *endings)


def _override_base_dir(config_map):
    if "config_dir" in config_map:
        return config_map["config_dir"]
    return None


def get_overrides_root(base_dir=None, config_map=None):
    """
    Get the root path for override files.

    Arguments
    base_dir - The base directory to search in.
    config_map - A configuration map.  If provided, this will override
                 base_dir.
    """
    if config_map:
        base_dir = _override_base_dir(config_map)
    return _make_path(base_dir, "overrides.d")


