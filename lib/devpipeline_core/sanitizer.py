#!/usr/bin/python3

"""Code related to project sanitization."""

import re

import devpipeline_core.plugin


def _sanitize_empty_depends(configuration, error_fn):
    for name, component in configuration.items():
        for dep in component.get_list("depends"):
            if not dep:
                error_fn("Empty dependency in {}".format(name))


_IMPLICIT_PATTERN = re.compile(r"\$\{([a-z_\-0-9\.]+):.+\}")


def _check_implicit_depends(component, dependencies, key, error_fn):
    val = component.get(key, raw=True)
    match = _IMPLICIT_PATTERN.search(val)
    if match:
        dep = match.group(1)
        if dep not in dependencies:
            error_fn(
                "{}:{} has an implicit dependency on {}".format(
                    component.name, key, dep
                )
            )


def _sanitize_implicit_depends(configuration, error_fn):
    for name, component in configuration.items():
        del name
        component_deps = component.get_list("depends")
        for key in component:
            _check_implicit_depends(component, component_deps, key, error_fn)


_SANITIZERS = devpipeline_core.plugin.query_plugins("devpipeline.config_sanitizers")


def sanitize(configuration, error_fn):
    """
    Run all availalbe sanitizers across a configuration.

    Arguments:
    configuration - a full project configuration
    error_fn - A function to call if a sanitizer check fails.  The function
               takes a single argument: a description of the problem; provide
               specifics if possible, including the componnet, the part of the
               configuration that presents an issue, etc..
    """
    for name, sanitize_fn in _SANITIZERS.items():
        sanitize_fn(configuration, lambda warning, n=name: error_fn(n, warning))
