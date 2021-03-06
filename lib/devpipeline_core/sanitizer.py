#!/usr/bin/python3

"""Code related to project sanitization."""

import re

import devpipeline_core.plugin

_DEPENDS_KEY_PATTERN = re.compile(r"^depends\..+")


def _get_depends_keys(configuration):
    return [key for key in configuration.keys() if _DEPENDS_KEY_PATTERN.match(key)]


def _sanitize_empty_depends(configuration, error_fn):
    for name, component in configuration.items():
        depends_keys = _get_depends_keys(component)
        for depends_key in depends_keys:
            for dep in component.get_list(depends_key):
                if not dep:
                    error_fn("Empty dependency in {}:{}".format(name, depends_key))


_IMPLICIT_PATTERN = re.compile(r"\$\{([a-z_\-0-9\.]+):.+\}")


def _check_implicit_depends(component, depends_keys, key, error_fn):
    val = component.get(key, raw=True)
    match = _IMPLICIT_PATTERN.search(val)
    if match:
        dep = match.group(1)
        for depends_key in depends_keys:
            if dep in component.get_list(depends_key):
                return None
        # not found in any of the depends keys
        error_fn(
            "{}:{} has an implicit dependency on {}".format(component.name, key, dep)
        )
    return None


def _sanitize_implicit_depends(configuration, error_fn):
    for name, component in configuration.items():
        del name
        depends_keys = _get_depends_keys(component)
        for key in component:
            _check_implicit_depends(component, depends_keys, key, error_fn)


def _sanitize_legacy_depends(configuration, error_fn):
    for name, component in configuration.items():
        if "depends" in component:
            if not _get_depends_keys(component):
                error_fn("{} uses a deprecated key (depends)".format(name))


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
