#!/usr/bin/python3

"""
Handle loading dev-pipeline plugins.
"""

import pkg_resources


def query_plugins(entry_point_name):
    """
    Find everything with a specific entry_point.  Results will be returned as a
    dictionary, with the name as the key and the entry_point itself as the
    value.

    Arguments:
    entry_point_name - the name of the entry_point to populate
    """
    entries = {}
    for entry_point in pkg_resources.iter_entry_points(entry_point_name):
        entries[entry_point.name] = entry_point.load()
    return entries
