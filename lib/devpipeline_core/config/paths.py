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
