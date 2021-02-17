# -*- coding: utf-8 -*-
import uuid

import pickle

from packratt.cache import Cache


def test_cache_multiton(tmp_path_factory):
    cache_dir = tmp_path_factory.mktemp("cache")
    cache_dir2 = tmp_path_factory.mktemp("cache2")
    # Test that we get the same object when creating with the same cache_dir
    assert Cache(cache_dir) is Cache(cache_dir)

    # Test that we get the same object when unpickling with the same cache_dir
    assert pickle.loads(pickle.dumps(Cache(cache_dir))) is Cache(cache_dir)

    # Sanity check
    assert Cache(cache_dir) is not Cache(cache_dir2)


def test_cache(test_cache):
    key = "/ms/wsrt/wst/ms.tar.gz"
    entry = {"url": "ftp://elwood.ru.ac.za/pub/sjperkins/wsrt.ms.tar.gz",
             "hash": uuid.uuid4().hex,
             "filename": "wsrt.ms.tar.gz"}

    test_cache[key] = entry
    cmp_entry = entry.copy()
    cmp_entry['dir'] = test_cache.cache_dir / test_cache.key_dir(key)

    assert cmp_entry == test_cache[key]
