#!/usr/bin/python3

"""Functionality related to environment configuration"""

import os
import re

_ENV_PATTERN = re.compile(R"env.(\w+)")


def get_env_list(config_map):
    """
    Retrieve a list of environemnt variables a configuration will modify.

    The list of variables will include anything in a configuration (including
    in extra configuration files) that can alter the environment.  The list
    will include only the variable names, not the env prefix.

    Arguments
    config_map - A configuration map.
    """
    env_adjustments = {}
    #for source in _SOURCE_FUNCTIONS:
        #source(config_map, env_adjustments)
    return env_adjustments.keys()


def create_environment(config_map):
    """
    Create a modified environment.

    Arguments
    config_map - A configuration map.
    """
    def _apply_override(adjustment, ret):
        upper_key = adjustment.upper()
        initial_value = config_map["current_config"].get(
            "env.{}".format(adjustment))
        if not initial_value:
            initial_value = ret.get(upper_key)
        new_value = devpipeline_core.config.modifier.modify_everything(
            initial_value, config_map,
            "env.{}".format(adjustment), os.pathsep)
        if new_value:
            ret[upper_key] = new_value
        else:
            ret.pop(upper_key, None)

    env_adjustments = get_env_list(config_map)
    if env_adjustments:
        ret = os.environ.copy()
        for adjustment in env_adjustments:
            _apply_override(adjustment, ret)
        return ret
    return os.environ
