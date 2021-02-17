# -*- coding: utf-8 -*-

from pathlib import Path

import yaml
from jsonschema import validate

import packratt
from packratt.directories import user_config_dir

SCHEMA_PATH = Path(Path(packratt.__file__).parent,
                   "conf", "registry-schema.yaml")

# Open the schema file
with open(SCHEMA_PATH, "r") as f:
    SCHEMA = yaml.safe_load(f)

# Create registry and entry schemas
REGISTRY_SCHEMA = {**SCHEMA, "$ref": "#/definitions/registry"}
ENTRY_SCHEMA = {**SCHEMA, "entry": {"type": {"$ref": "/definitions/entry"}}}

del SCHEMA_PATH


USER_REGISTRY = Path(user_config_dir, "registry.yaml")


def load_registry(filename=None):
    path = Path(Path(packratt.__file__).parent, "conf", "registry.yaml")

    with open(path, "r") as f:
        registry = yaml.safe_load(f)

    if USER_REGISTRY.is_file():
        with open(USER_REGISTRY, "r") as f:
            registry.update(yaml.safe_load(f))

    validate(registry, schema=REGISTRY_SCHEMA)

    return registry
