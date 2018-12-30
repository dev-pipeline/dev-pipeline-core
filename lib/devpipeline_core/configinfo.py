#!/usr/bin/python3

"""
Functionality and types to support configuration state while executing
Commands.
"""


class ConfigInfo:
    """
    A class to abstract metadata about a running Command.
    """

    def __init__(self, executor):
        self._executor = executor
        self._current_config = None
        self._current_env = None

    @property
    def executor(self):
        """
        Retrieve the executor used by the running Command.
        """
        return self._executor

    @property
    def config(self):
        """
        Retrieve the configuration for the component being processed.
        """
        return self._current_config

    @config.setter
    def config(self, config):
        """
        Set the currently processed component's configuration.
        """
        self._current_config = config

    @property
    def env(self):
        """
        Retrieve the processed environment settings for the current component;
        the enviornment is a dictionary-like object.
        """
        return self._current_env

    @env.setter
    def env(self, env):
        """
        Set the current componnet's processed environment variables.
        """
        self._current_env = env
