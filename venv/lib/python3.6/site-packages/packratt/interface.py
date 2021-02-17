import logging
from pathlib import Path
import shutil

from packratt.cache import validate_entry, get_cache, set_cache
from packratt.downloads import downloaders

log = logging.getLogger(__name__)


def get(key, destination, entry=None):
    """
    Parameters
    ----------
    key : str
        Retrieval key
    destination : str or Path
        Path in which to unarchive the data product
    entry : None or dict
        dictionary entry describing the data product, if not in the registry.
        Defaults to None in which case the entry must be in the registry.
    """

    cache = get_cache()

    if entry is None:
        try:
            entry = cache[key]
        except KeyError:
            raise ValueError("%s is not in the registry" % key)
    elif isinstance(entry, dict):
        validate_entry(entry)
        cache[key] = entry
        set_cache(cache)
        entry = cache[key]
    else:
        raise TypeError("entry must be None or dict")

    if not isinstance(destination, Path):
        destination = Path(destination)

    if destination.exists() and not destination.is_dir():
        # Don't overwrite existing files
        raise ValueError(
            "Target %s exists and is not a directory" % destination)
    else:
        # Create the destination directory
        destination.mkdir(parents=True, exist_ok=True)

    filename = entry['dir'] / Path(key).name

    if filename.exists():
        # TODO(sjperkins):
        # This is a massive assumption, what about partial downloads etc.
        sha256_hash = entry['hash']
    else:
        # Download to the destination
        sha256_hash = downloaders(entry['type'], key, entry)

        if not sha256_hash == entry['hash']:
            raise ValueError("sha256hash does not agree. %s vs %s"
                             % (sha256_hash, entry['hash']))

    shutil.unpack_archive(str(filename), destination)

    return sha256_hash
