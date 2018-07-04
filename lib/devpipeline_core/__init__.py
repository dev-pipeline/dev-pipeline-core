#!/usr/bin/python3

"""The main module for devpipeline"""

import devpipeline_core.executor

EXECUTOR_TYPES = {
    "dry-run": devpipeline_core.executor.DryRunExecutor,
    "quiet": devpipeline_core.executor.QuietExecutor,
    "silent": devpipeline_core.executor.SilentExecutor,
    "verbose": devpipeline_core.executor.VerboseExecutor
}
