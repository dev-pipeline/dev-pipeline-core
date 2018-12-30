#!/usr/bin/python3
"""This module has tool helper classes and functions."""


class SimpleTool:
    """
    This class implements a simple tool for the dev-pipeline infrastructure.
    It handles setting the environment and working with an executor so clients
    only have to worry about the arguments to the subprocess module.
    """

    # pylint: disable=too-few-public-methods
    def __init__(self, current_target, real):
        self.env = current_target.env
        self.executor = current_target.executor
        self.name = current_target.config.name
        self.real = real

    def _call_helper(self, step, helper_fn, *fn_args, **fn_kwargs):
        self.executor.message("{} {}".format(step, self.name))
        cmds = helper_fn(*fn_args, **fn_kwargs)
        if cmds:
            self.executor.execute(self.env, *cmds)
        else:
            self.executor.message("\t(Nothing to do)")


class MissingToolKey(Exception):
    """
    An exception to emit if a component doesn't have a required tool configured.
    """

    def __init__(self, key, component):
        super().__init__()
        self._key = key
        self._component_name = component.name

    def __str__(self):
        return "'{}' unspecified in {}".format(self._key, self._component_name)


def _choose_key(config, keys):
    for key in keys:
        if key in config:
            return key
    return keys[0]


def choose_tool_key(full_configuration, keys):
    """
    Select the key for a tool from a list of supported tools.

    This function is designed to help when multiple keys can be used to specify
    an option (e.g., during migration from one name to another).  The values in
    keys should be ordered based on preference, as that's the order they'll be
    checked.  If anything other than the first entry is selected, a warning
    will be displayed telling the user to migrate their configuration.

    Arguments:
    full_configuration - the full configuration for a run of the project
    keys - a list of keys to consider
    """
    tool_key = _choose_key(full_configuration.config, keys)
    if tool_key != keys[0]:
        full_configuration.executor.warning(
            "{} is deprecated; migrate to {}".format(tool_key, keys[0])
        )
    return tool_key


def tool_builder(component, key, tool_map, *args):
    """This helper function initializes a tool with the given args."""
    # pylint: disable=protected-access
    tool_name = component.get(key)
    if tool_name:
        tool_fn = tool_map.get(tool_name)
        if tool_fn:
            return tool_fn[0](*args)
        else:
            raise Exception(
                "Unknown {} '{}' for {}".format(key, tool_name, component.name)
            )
    else:
        raise MissingToolKey(key, component)


class _NullJoiner:
    """A class to handle non-joinable values."""

    # pylint: disable=too-few-public-methods
    def __init__(self, component_name, key):
        self._component_name = component_name
        self._key = key

    def join(self, vals):
        """
        Either return the non-list value or raise an Exception.

        Arguments:
        vals - a list of values to process
        """
        if len(vals) == 1:
            return vals[0]
        raise Exception(
            "Too many values for {}:{}".format(self._component_name, self._key)
        )


class ListSeparator:
    """A class to that does nothing; it exists to provie a join method."""

    # pylint: disable=too-few-public-methods
    def join(self, vals):
        """Return vals without mofication."""
        # pylint: disable=no-self-use
        return vals


def args_builder(prefix, current_target, args_dict, value_found_fn):
    """
    Process arguments a tool cares about.

    Since most tools require configuration, this function helps deal with the
    boilerplate.  Each option will be processed based on all modifications
    supported by dev-pipeline (i.e., profiles and overrides) in the proper
    order.

    Arguments:
    prefix -- The prefix for each argument.  This will be applied to
              everything in args_dict.
    current_target -- Information about the current target being processed.
    args_dict -- Something that acts like a dictionary.  The keys should be
                 options to deal with and the value should be the separtor
                 value the option requires.  The separator can be any type
                 that has a join method, or None if lists are supported for
                 that key.
    value_found_fn -- A function to call when a match is found.
    """
    current_config = current_target.config
    for key, separator in args_dict.items():
        option = "{}.{}".format(prefix, key)
        value = current_config.get_list(option)
        if value:
            if separator is None:
                separator = _NullJoiner(current_config.name, option)
            value_found_fn(separator.join(value), key)


def build_flex_args_keys(components):
    """
    Helper function to build a list of options.

    Some tools require require variations of the same options (e.g., cflags
    for debug vs release builds), but manually creating those options is
    cumbersome and error-prone.  This function handles that work by combining
    all possible comintations of the values in components.

    Arguments
    components -- A list of lists that should be combined to form options.
    """

    def _prepend_first(components, sub_components):
        ret = []
        for first in components[0]:
            for sub_component in sub_components:
                ret.append("{}.{}".format(first, sub_component))
        return ret

    if len(components) > 1:
        sub_components = build_flex_args_keys(components[1:])
        return _prepend_first(components, sub_components)
    elif len(components) == 1:
        return components[0]
    return []
