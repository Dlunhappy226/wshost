from wshost import statuses
from wshost import headers
from wshost import etags
import mimetypes
import json
import os


class Response:
    def __init__(self, content, header=[], status=statuses.OK, connection=True, content_type="", etag=False, no_content=False):
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
    def __init__(self, url, status=statuses.FOUND, header=[], connection=True):
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


def read(filename):
    file = open(filename, "rb")
    content = file.read()
    file.close()
    return content

def request_handle(request):
    method = request["method"].lower()
    path = request["path"]
    root = request["config"].root_directory
    file = path.split("/")
    filename = file[-1]
    
    if method in ["get", "head"]:
        try:
            if filename == "":
                path = f"{path}/index.html"
                filename = "index.html"

            elif os.path.isdir(f"{root}{path}"):
                content = b""
                return Redirect(f"{path}/")

            if not os.path.exists(f"{root}{path}"):
                return Error(statuses.NOT_FOUND)

            content = read(f"{root}{path}")
            content_type = mimetypes.guess_type(filename)[0]

            if content_type == None:
                content_type = "text/plain"

            last_modified = etags.get_last_modified(f"{root}{path}")
            etag = etags.generate_etag(content)

            if etags.check_etag(request, etag):
                return etags.not_modified(content, last_modified)
            
        except PermissionError:
            return Error(statuses.NOT_FOUND)

        try:
            content = content.decode()
        except UnicodeDecodeError:
            pass

        return Response(content, header=[("Last-Modified", last_modified)], content_type=content_type, etag=True, no_content=(method == "head"))
    else:
        return Error(statuses.METHOD_NOT_ALLOWED)

def encode_response(content, status=statuses.OK, header=[], connection=True, content_type="", etag=False, no_content=False):
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

    if (not headers.check_header(header, "Content-Length")) and (not ((len(content) == 0) and (status == statuses.OK))):
        default_header.append(("Content-Length", len(content)))

    if (len(content) == 0) and (status == statuses.OK):
        status = statuses.NO_CONTENT

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
