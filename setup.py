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
            "dry-run = devpipeline_core.executor:DryRunExecutor",
            "quiet = devpipeline_core.executor:QuietExecutor",
            "silent = devpipeline_core.executor:SilentExecutor",
            "verbose = devpipeline_core.executor:VerboseExecutor"
        ],

        'devpipeline.resolvers': [
            "deep = devpipeline_core.resolve:process_dependencies",
            "none = devpipeline_core.resolve:process_none",
            "reverse = devpipeline_core.resolve:process_reverse"
        ]
    },

    author="Stephen Newell",
    description="Core libraries for dev-pipeline",
    license="BSD-2"
)
