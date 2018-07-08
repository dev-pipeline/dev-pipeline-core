#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name="dev-pipeline-core",
    version="0.2.0",
    package_dir={
        "": "lib"
    },
    packages=find_packages("lib"),

    entry_points={
        'devpipeline.executors': [
            "dry-run = devpipeline_core.executor:_DRYRUN_EXECUTOR",
            "quiet = devpipeline_core.executor:_QUIET_EXECUTOR",
            "silent = devpipeline_core.executor:_SILENT_EXECUTOR",
            "verbose = devpipeline_core.executor:_VERBOSE_EXECUTOR"
        ],

        'devpipeline.resolvers': [
            "deep = devpipeline_core.resolve:_DEEP_RESOLVER",
            "none = devpipeline_core.resolve:_NONE_RESOLVER",
            "reverse = devpipeline_core.resolve:_REVERSE_RESOLVER"
        ]
    },

    author="Stephen Newell",
    description="Core libraries for dev-pipeline",
    license="BSD-2"
)
