#!/usr/bin/python3

import re

import devpipeline_core.plugin


def _sanitize_empty_depends(configuration, error_fn):
    for component_name in configuration.components():
        component = configuration.get(component_name)
        for dep in component.get_list("depends"):
            if not dep:
                error_fn("Empty dependency in {}".format(component_name))


_SANITIZERS = devpipeline_core.plugin.query_plugins(
    "devpipeline.config_sanitizers")


def sanitize(configuration, error_fn):
    for name, fn in _SANITIZERS.items():
        fn(configuration, lambda warning, n=name: error_fn(n, warning))
