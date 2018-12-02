#!/usr/bin/python3

"""Functions related to configuration paths"""

import os.path


def make_path(config, *endings):
    config_dir = config.get("dp.config_dir")
    return os.path.join(config_dir, *endings)
