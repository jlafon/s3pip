import os
import mimetypes
import sys
import urlparse
from StringIO import StringIO

try:
    import pip
    from pip._vendor.requests.adapters import BaseAdapter, HTTPAdapter
    from pip._vendor.requests.structures import CaseInsensitiveDict
    from pip._vendor.requests import Response
    from pip.log import logger
    from pip.download import PipSession
    from pip.download import LocalFSResponse
except ImportError as err:
    sys.stderr.write('Error: pip<=1.5 is required ({})'.format(err))

try:
    from boto.s3.connection import S3Connection
except ImportError as err:
    sys.stderr.write('Error: boto is required ({})'.format(err))


class S3RawResponse(LocalFSResponse):
    def __init__(self, content):
        self.fileobj = StringIO(content)


class S3Response(Response):
    def __init__(self, raw, url, length, content_type):
        super(S3Response, self).__init__()
        self.status_code = 200
        self.raw = S3RawResponse(raw)
        self.headers = CaseInsensitiveDict({
            "Content-Type": content_type,
            "Content-Length": length,
        })
        self.url = url


class S3Adapter(BaseAdapter):
    def send(self, request, **kwargs):
        conn = S3Connection(is_secure=True)
        bucket_name = os.getenv('S3_PIP_BUCKET_NAME')
        update_indexes = os.getenv('S3_PIP_COMPARE_CACHE')
        bucket = conn.get_bucket(bucket_name)
        keyname = urlparse.urlparse(request.url).path
        html = False
        if keyname.endswith("/"):
            keyname += "index.html"
            html = True
        key = bucket.get_key(keyname)
        if html:
            content_type = "text/html"
        else:
            content_type = mimetypes.guess_type(request.url)[0] or "text/plain"
        if key is None:
            pypi_resp = HTTPAdapter().send(request, **kwargs)
            if pypi_resp.status_code != 200:
                return pypi_resp
            content = pypi_resp.content
            resp = S3Response(content, request.url, len(content), content_type)
            self.s3_sync(request.url, content, bucket, pypi_resp.headers.get('x-pypi-last-serial'))
            return resp
        logger.notify("Found item in S3 {0}".format(keyname))
        resp = S3Response(key.get_contents_as_string(), request.url, key.size, content_type)
        if update_indexes:
            pypi_resp = HTTPAdapter().send(request, **kwargs)
            if pypi_resp.headers['x-pypi-last-serial'] > key.get_metadata('x-pypi-last-serial'):
                content = pypi_resp.content
                resp = S3Response(content, request.url, len(content), content_type)
                self.s3_sync(request.url, content, bucket, pypi_resp.headers['x-pypi-last-serial'])
        return resp

    def close(self):
        pass

    def s3_sync(self, url, content, bucket, cache_index=None):
        parts = urlparse.urlparse(url)
        keyname = parts.path
        if keyname.endswith("/"):
            keyname += "index.html"
        key = bucket.new_key(keyname)
        if cache_index is not None:
            key.set_metadata('x-pypi-last-serial', cache_index)
        logger.notify("Synchronizing {0} to s3".format(keyname))
        key.set_contents_from_string(content)


def request(self, method, url, *args, **kwargs):
    self.mount('https://', S3Adapter())
    self.mount('http://', S3Adapter())
    return super(PipSession, self).request(method, url, *args, **kwargs)


def main():
    bucket_name = os.getenv('S3_PIP_BUCKET_NAME')
    if bucket_name is not None:
        pip.download.PipSession.request = request

    pip.main()

if __name__ == '__main__':
    main()