#!/usr/bin/python3

import re

import devpipeline_core.plugin


def _sanitize_empty_depends(configuration, error_fn):
    for component_name in configuration.components():
        component = configuration.get(component_name)
        for dep in component.get_list("depends"):
            if not dep:
                error_fn("Empty dependency in {}".format(component_name))


_IMPLICIT_PATTERN = re.compile(R'\$\{([a-z_\-0-9\.]+):.+\}')


def _sanitize_implicit_depends(configuration, error_fn):
    for component_name in configuration.components():
        component = configuration.get(component_name)
        component_deps = component.get_list("depends")
        for key in component:
            val = component.get(key, raw=True)
            m = _IMPLICIT_PATTERN.search(val)
            if m:
                dep = m.group(1)
                if dep not in component_deps:
                    error_fn(
                        "{}:{} has an implicit dependency on {}".format(
                            component_name, key, dep))


_SANITIZERS = devpipeline_core.plugin.query_plugins(
    "devpipeline.config_sanitizers")


def sanitize(configuration, error_fn):
    for name, fn in _SANITIZERS.items():
        fn(configuration, lambda warning, n=name: error_fn(n, warning))
