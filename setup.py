#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name="dev-pipeline-core",
    version="0.2.0",
    package_dir={
        "": "lib"
    },
    packages=find_packages("lib"),

    author="Stephen Newell",
    description="Core libraries for dev-pipeline",
    license="BSD-2"
)
