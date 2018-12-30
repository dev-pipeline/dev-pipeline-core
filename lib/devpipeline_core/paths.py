#!/usr/bin/python3

"""Functions related to configuration paths"""

import os.path


def make_path(config, *endings):
    """
    Create a path based on component configuration.

    All paths are relative to the component's configuration directory; usually
    this will be the same for an entire session, but this function supuports
    component-specific configuration directories.

    Arguments:
    config - the configuration object for a component
    endings - a list of file paths to append to the component's configuration
              directory
    """
    config_dir = config.get("dp.config_dir")
    return os.path.join(config_dir, *endings)
