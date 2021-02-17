from jsonschema import validate

from packratt.registry import REGISTRY_SCHEMA
from packratt.tests.conftest import USER_REGISTRY_CONTENT


def test_schema():
    validate(
        {
            "/ms/vla/vla012345.ms": {
                "type": "url",
                "url": "https://blah.org/vla012345.ms",
                "hash": "123456",
                "filename": "vla012345.ms",
            },
            "/ms/vla/vla543210.ms": {
                "type": "google",
                "file_id": "123456",
                "hash": "123456",
                "filename": "vla012345.ms",
            },
        },
        schema=REGISTRY_SCHEMA)


def test_user_registry(registry):
    user_key = '/test/ms/2020-06-04/google/test_user_registry_ms.tar.gz'

    assert registry[user_key] == USER_REGISTRY_CONTENT[user_key]
