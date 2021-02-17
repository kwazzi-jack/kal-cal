from contextlib import contextmanager
from ftplib import FTP
import hashlib
import logging
from pathlib import Path
import shutil
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from packratt.dispatch import Dispatch

log = logging.getLogger(__name__)

downloaders = Dispatch()

# 32k chunks
CHUNK_SIZE = 2**15


@contextmanager
def retry_strategy():
    retry = Retry(
        total=5,
        status_forcelist=[413, 429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        yield session
    finally:
        session.close()


@contextmanager
def open_and_hash_file(filename):
    sha256hash = hashlib.sha256()
    size = 0

    if filename.is_file():
        # File exists, hash contents and determine existing size
        # This also moves the file pointer to the end of the file
        f = open(filename, "rb+")

        while True:
            chunk = f.read(CHUNK_SIZE)

            if not chunk:
                break

            sha256hash.update(chunk)
            size += len(chunk)
    else:
        # Open a new file for writing
        f = open(filename, "wb")

    try:
        yield size, sha256hash, f
    finally:
        f.close()


def requests_partial_download(key, entry, url, session,
                              response, params=None):
    filename = Path(key).name
    part_filename = entry['dir'] / '.'.join((filename, 'partial'))
    filename = entry['dir'] / filename

    if params is None:
        params = {}

    with open_and_hash_file(part_filename) as (size, sha256hash, f):
        if size > 0:
            log.info("Resuming download of %s at %d", filename, size)
            # Some of this file has already been downloaded
            # Request the rest of it
            total_size = int(response.headers['Content-Length'])
            response.close()
            headers = {'Range': 'bytes=%d-%d' % (size, total_size)}
            response = session.get(url, params=params,
                                   headers=headers, stream=True)

        if response.status_code != 416:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise Exception(e)

            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    sha256hash.update(chunk)
                    f.write(chunk)

    shutil.move(part_filename, filename)
    return sha256hash.hexdigest()


@downloaders.register("google")
def download_google_drive(key, entry):
    url = "https://drive.google.com/uc?export=download"
    params = {'id': entry['file_id']}

    with retry_strategy() as session:
        response = session.get(url, params=params, stream=True)

        try:
            # Look for a token indicating a large file
            # Re-request with confirmation token
            for k, v in response.cookies.items():
                if k.startswith('download_warning'):
                    params['confirm'] = v
                    response.close()
                    response = session.get(url, params=params, stream=True)
                    break

            return requests_partial_download(key, entry, url,
                                             session, response,
                                             params=params)
        finally:
            response.close()


def download_ftp(key, entry, url):
    filename = Path(key).name
    part_filename = entry['dir'] / '.'.join((filename, 'partial'))
    filename = entry['dir'] / filename

    with open_and_hash_file(part_filename) as (size, sha256hash, f):
        if size > 0:
            log.info("Resuming download of %s at %d", part_filename, size)

        ftp = FTP(url.hostname)

        def callback(data):
            f.write(data)
            sha256hash.update(data)

        try:
            ftp.login(url.username, url.password)
            ftp.retrbinary("RETR %s" % url.path, callback,
                           blocksize=CHUNK_SIZE, rest=size)

            shutil.move(part_filename, filename)
        finally:
            ftp.quit()

        return sha256hash.hexdigest()


@downloaders.register("url")
def download_url(key, entry):
    # requests doesn't handle ftp
    parsed_url = urlparse(entry['url'])

    if parsed_url.scheme == "ftp":
        return download_ftp(key, entry, parsed_url)

        # Use requests for (presumably) http cases
        with retry_strategy() as session:
            response = session.get(entry['url'], stream=True)

            try:
                return requests_partial_download(key, entry, entry['url'],
                                                 session, response)
            finally:
                response.close()
