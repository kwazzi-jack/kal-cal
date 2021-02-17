from packratt.cache import get_cache, set_cache, Cache
from packratt.registry import load_registry

from unittest.mock import patch
import pytest
import yaml


@pytest.fixture(scope="session", autouse=True)
def global_test_cache(tmp_path_factory):
    cache_dir = tmp_path_factory.mktemp('cache')
    set_cache(Cache(cache_dir))


@pytest.fixture
def test_cache(tmp_path_factory):
    cache_dir = tmp_path_factory.mktemp('cache')

    old_cache = get_cache()

    try:
        new_cache = Cache(cache_dir)
        set_cache(new_cache)
        yield new_cache
    finally:
        set_cache(old_cache)


USER_REGISTRY_CONTENT = {
    '/test/ms/2020-06-04/google/test_user_registry_ms.tar.gz': {
        'type': 'google',
        'file_id': '1wjZoh7OAIVEjYuTmg9dLAFiLoyehnIcL',
        'hash': '4d548b22331fb3cd3256b1b4f37a41cf',
        'description': 'Small testing Measurement Set, stored on Google Drive',
    }
}


@pytest.fixture(scope="session")
def registry(tmp_path_factory):
    conf = tmp_path_factory.mktemp('conf') / "registry.yaml"

    with open(conf, "w") as f:
        f.write(yaml.safe_dump(USER_REGISTRY_CONTENT))

    with patch('packratt.registry.USER_REGISTRY', conf):
        return load_registry()
