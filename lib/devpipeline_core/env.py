#!/usr/bin/python3

"""Functionality related to environment configuration"""

import os


def _prepend_env(config, base_key, current_value):
    prepend_key = "env.{}.prepend".format(base_key)
    if prepend_key in config:
        prepend_value = os.pathsep.join(config.get_list(prepend_key))
        if current_value is not None:
            return "{}{}{}".format(prepend_value, os.pathsep, current_value)
        return prepend_value
    return current_value


def _append_env(config, base_key, current_value):
    append_key = "env.{}.append".format(base_key)
    if append_key in config:
        append_value = os.pathsep.join(config.get_list(append_key))
        if current_value is not None:
            return "{}{}{}".format(current_value, os.pathsep, append_value)
        return append_value
    return current_value


def create_environment(config_map):
    """
    Create a modified environment.

    Arguments
    config_map - A configuration map.
    """
    ret = os.environ.copy()
    current_config = config_map["current_config"]
    for env in current_config.get_list("dp.env_list"):
        real_env = env.upper()
        value = os.environ.get(real_env)
        value = _prepend_env(current_config, env, value)
        value = _append_env(current_config, env, value)
        if value is not None:
            ret[real_env] = value
        else:
            # either an override or erase
            key = "env.{}".format(env)
            if key in current_config:
                ret[real_env] = os.pathsep.join(current_config.get_list(key))
            else:
                if real_env in ret:
                    del ret[real_env]
    return ret
