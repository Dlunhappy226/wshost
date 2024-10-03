from wshost import status
from wshost import headers
from wshost import etags
import json


class Response:
    def __init__(self, content, header=[], status=status.OK, connection=True, content_type="", etag=False, no_content=False):
        self.content = content
        self.header = header
        self.status = status
        self.connection = connection
        self.content_type = content_type
        self.etag = etag
        self.no_content = no_content


class RawResponse:
    def __init__(self, response, connection=True):
        self.response = response
        self.connection = connection


class Redirect:
    def __init__(self, url, status=status.FOUND, header=[], connection=True):
        self.url = url
        self.status = status
        self.header = header
        self.connection = connection


class Route:
    def __init__(self, path):
        self.path = path
 

class Error:
    def __init__(self, error, passing=False):
        self.error = error
        self.passing = passing


def encode_response(content, status=status.OK, header=[], connection=True, content_type="", etag=False, no_content=False):
    if type(content) in [list, dict]:
        content = json.dumps(content)

    if type(content) == str:
        content = content.encode()
        byte = False
    else:
        byte = True

    default_header = []

    if content_type and (not headers.check_header(header, "Content-Type")):
        default_header.append(("Content-Type", content_type))

    if (not headers.check_header(header, "Content-Length")) and (not ((len(content) == 0) and (status == status.OK))):
        default_header.append(("Content-Length", len(content)))

    if (len(content) == 0) and (status == status.OK):
        status = status.NO_CONTENT

    default_header += header

    if not headers.check_header(header, "Connection"):
        if connection:
            default_header.append(("Connection", "keep-alive"))
        else: 
            default_header.append(("Connection", "close"))

    if etag and (not headers.check_header(header, "ETag")):
       default_header.append(("ETag", etags.generate_etag(content)))

    if byte and (not headers.check_header(header, "Accept-Ranges")):
        default_header.append(("Accept-Ranges", "bytes"))

    if no_content:
        content = b""

    return headers.encode(status, default_header) + content

def unauthorized(realm="Acess to the staging site."):
    return Response("", status=status.UNAUTHORIZED, header=[("WWW-Authenticate", f"Basic realm={realm}")])

def not_modified(content, last_modified):
    return Response(content, status=status.NOT_MODIFIED, header=[("Last-Modified", last_modified)], etag=True, no_content=False)

def forbidden():
    return Error(status.FORBIDDEN)
