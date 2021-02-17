# -*- coding: utf-8 -*-
from hashlib import sha224
from pathlib import Path
from threading import Lock
import weakref

from jsonschema import validate, ValidationError
import yaml

from packratt.directories import user_cache_dir
from packratt.registry import load_registry, ENTRY_SCHEMA


def validate_entry(entry):
    try:
        return validate(entry, ENTRY_SCHEMA)
    except ValidationError as e:
        raise ValueError("%s is not a valid entry" % entry) from e


_cache_lock = Lock()
_cache_cache = weakref.WeakValueDictionary()


class CacheMetaClass(type):
    """
    https://en.wikipedia.org/wiki/Multiton_pattern

    """
    def __call__(cls, cache_dir):
        with _cache_lock:
            try:
                return _cache_cache[cache_dir]
            except KeyError:
                instance = type.__call__(cls, cache_dir)
                _cache_cache[cache_dir] = instance
                return instance


class Cache(metaclass=CacheMetaClass):
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.registry = load_registry()

    def __reduce__(self):
        return (Cache, (self.cache_dir,))

    @staticmethod
    def key_dir(key) -> Path:
        h = sha224(key.encode('ascii')).hexdigest()
        return Path(h[0:2], h[2:4], h[4:6], h[6:])

    def cache_key_dir(self, key) -> Path:
        """
        Parameters
        ----------
        key : str
            Cache entry key

        Returns:
        path : :class:`Path`
            Path to the cache entry
        """
        return Path(self.cache_dir) / self.key_dir(key)

    def __setitem__(self, key, value):
        """
        Inserts a Cache entry

        Parameters
        ----------
        key : str
            Cache entry key
        value : dict
            Cache entry
        """
        if not isinstance(value, dict):
            raise TypeError("value must be a dict")

        # Is this a valid cache entry dictionary?
        validate_entry(value)

        entry_dir = self.cache_key_dir(key)

        try:
            entry_dir.mkdir(parents=True, exist_ok=True)
        except FileExistsError as e:
            raise ValueError("Already exists") from e

        with open(entry_dir / "entry.yaml", "w") as f:
            f.write(yaml.safe_dump(value))

    def __getitem__(self, key):
        """
        Retrieves a cache entry

        Parameters
        ----------
        key : str
            Cache entry key

        Returns
        -------
        entry : :class:`CacheEntry`
            Cache entry
        """
        entry_dir = self.cache_key_dir(key)

        # Try obtain the entry from the registry first
        # It's the primary source of truth
        try:
            entry = self.registry[key]
        except KeyError:
            # Look for an entry file as the secondary source of truth
            entry_file = entry_dir / "entry.yaml"

            # Nothing, raise a KeyError
            if not entry_file.exists():
                raise KeyError(key)

            with open(entry_file, "r") as f:
                entry = yaml.safe_load(f)
        else:
            self.__setitem__(key, entry)

        entry['dir'] = entry_dir

        return entry


def cache_factory(cache_dir=None):
    if cache_dir is None:
        return Cache(cache_dir)

    return Cache(user_cache_dir)


app_cache = None


def get_cache():
    global app_cache

    if app_cache is None:
        app_cache = Cache(user_cache_dir)

    return app_cache


def set_cache(cache):
    global app_cache

    if not isinstance(cache, Cache):
        raise TypeError("cache must be of type Cache")

    app_cache = cache
