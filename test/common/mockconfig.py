#!/usr/bin/python3


class MockComponent:
    def __init__(self, name, config):
        self._name = name
        self._config = config

    @property
    def name(self):
        return self._name

    def get(self, key, raw=False, fallback=None):
        return self._config.get(key, fallback)

    def get_list(self, key, fallback=None, split=","):
        fallback = fallback or []
        raw = self.get(key, None)
        if raw:
            return [value.strip() for value in raw.split(split)]
        return fallback

    def __iter__(self):
        return iter(self._config)

    def __contains__(self, item):
        return item in self._config

    def __getitem__(self, key):
        return self.get(key)


class MockConfig:
    def __init__(self, config):
        self._config = config

    def keys(self):
        """Get a list of component names provided by a configuration."""
        return self._config.keys()

    def items(self):
        # return _CachedComponentIterator(self._config.sections(), self)
        pass

    def get(self, component):
        """Get a specific component to operate on"""
        config = self._config.get(component)
        if config is not None:
            return MockComponent(component, config)
        return None

    def __iter__(self):
        return iter(self._config)

    def __contains__(self, item):
        return item in self._config
