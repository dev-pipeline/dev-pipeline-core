#!/usr/bin/python3


class ConfigInfo:
    def __init__(self, executor):
        self._executor = executor
        self._current_config = None
        self._current_env = None

    @property
    def executor(self):
        return self._executor

    @property
    def config(self):
        return self._current_config

    @config.setter
    def config(self, config):
        self._current_config = config

    @property
    def env(self):
        return self._current_env

    @env.setter
    def env(self, env):
        self._current_env = env
