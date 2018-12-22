#!/usr/bin/python3

"""Functionality related to environment configuration"""

import os


def _append_prepend_env(config, suffix_key, base_key, builder_string, current_value):
    env_key = "env.{}.{}".format(base_key, suffix_key)
    if env_key in config:
        env_value = os.pathsep.join(config.get_list(env_key))
        if current_value is not None:
            return builder_string.format(current_value, os.pathsep, env_value)
        return env_value
    return current_value


def _prepend_env(config, base_key, current_value):
    return _append_prepend_env(config, "prepend", base_key, "{2}{}{0}", current_value)


def _append_env(config, base_key, current_value):
    return _append_prepend_env(config, "append", base_key, "{}{}{}", current_value)


def create_environment(target_config):
    """
    Create a modified environment.

    Arguments
    config_map - A configuration map.
    """
    ret = os.environ.copy()
    for env in target_config.get_list("dp.env_list"):
        real_env = env.upper()
        value = os.environ.get(real_env)
        value = _prepend_env(target_config, env, value)
        value = _append_env(target_config, env, value)
        if value is not None:
            ret[real_env] = value
        else:
            # either an override or erase
            key = "env.{}".format(env)
            if key in target_config:
                ret[real_env] = os.pathsep.join(target_config.get_list(key))
            else:
                if real_env in ret:
                    del ret[real_env]
    return ret
