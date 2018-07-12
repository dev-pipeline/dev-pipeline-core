#!/usr/bin/python3

from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

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
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license="BSD-2",
    url="https://github.com/dev-pipeline/dev-pipeline-core",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: Utilities"
    ]
)
