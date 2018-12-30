#!/usr/bin/python3

"""
Functionality related to environment modification.
"""

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


def _apply_change(env_set, env_key, value, component_config):
    if value is not None:
        env_set[env_key] = value
    else:
        # either an override or erase
        key = "env.{}".format(env_key.lower())
        if key in component_config:
            env_set[env_key] = os.pathsep.join(component_config.get_list(key))
        else:
            if env_key in env_set:
                del env_set[env_key]


def create_environment(component_config):
    """
    Create a modified environment.

    Arguments
    component_config - The configuration for a component.
    """
    ret = os.environ.copy()
    for env in component_config.get_list("dp.env_list"):
        real_env = env.upper()
        value = os.environ.get(real_env)
        value = _prepend_env(component_config, env, value)
        value = _append_env(component_config, env, value)
        _apply_change(ret, real_env, value, component_config)
    return ret
