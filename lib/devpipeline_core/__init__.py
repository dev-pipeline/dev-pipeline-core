#!/usr/bin/python3

"""
Common functionality used by many dev-pipeline tooling.
"""

import devpipeline_core.plugin

EXECUTOR_TYPES = devpipeline_core.plugin.query_plugins("devpipeline.executors")
DEPENDENCY_RESOLVERS = devpipeline_core.plugin.query_plugins("devpipeline.resolvers")
