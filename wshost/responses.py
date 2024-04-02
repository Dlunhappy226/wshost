from wshost import headers
from wshost import errors
from wshost import etags
import mimetypes
import datetime
import json
import time
import os


class Response:
    def __init__(self, content, header=[], status=headers.OK, connection=True):
        self.content = content
        self.header = header
        self.status = status
        self.connection = connection


class RawResponse:
    def __init__(self, response, connection=True):
        self.response = response
        self.connection = connection


class Redirect:
    def __init__(self, url, status=headers.FOUND, header=[], connection=True):
        self.url = url
        self.status = status
        self.header = header
        self.connection = connection


class Route:
    def __init__(self, path, connection=True):
        self.path = path
        self.connection = connection
 

class Error:
    def __init__(self, error):
        self.error = error


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
    
    if method == "get" or method == "head":
        try:
            if filename == "":
                path = f"{path}/index.html"
                filename = "index.html"

            elif os.path.isdir(f"{root}{path}"):
                content = b""
                return Redirect(f"{path}/")

            if not os.path.exists(f"{root}{path}"):
                return Error(headers.NOT_FOUND)

            content = read(f"{root}{path}")
            status = headers.OK
            content_type = mimetypes.guess_type(filename)[0]
            if content_type == None:
                content_type = "text/plain"

            last_modified = etags.get_last_modified(f"{root}{path}")
            etag = etags.generate_etag(content)

            if etags.check_etag(request, etag):
                status = headers.NOT_MODIFIED
                content = b""

        except PermissionError:
            return Error(headers.NOT_FOUND)

        header = []

        if status != headers.NOT_MODIFIED:
            header.append(("Content-Type", content_type))

            if method == "get":
                header.append(("Content-Length", len(content)))
            else:
                content = b""

        header.append(("Last-Modified", last_modified))

        if status != headers.NOT_MODIFIED:
            try:
                content.decode()
            except UnicodeDecodeError:
                header.append(("Accept-Ranges", "bytes"))

        if "Connection" in request["header"] and request["header"]["Connection"] == "keep-alive":
            header.append(("Connection", "keep-alive"))
        else:
            header.append(("Connection", "close"))
        header.append(("ETag", etag))
        
        return RawResponse(headers.encode(status=status, headers=header) + content)
    else:
        return Error(headers.METHOD_NOT_ALLOWED)

def encode_response(content, status=headers.OK, header=[], connection=True):
    default_header = []

    if not headers.check_header(header, "Content-Length"):
        default_header.append(("Content-Length", len(content)))

    if type(content) == bytes and not headers.check_header(header, "Accept-Ranges"):
        default_header.append(("Accept-Ranges", "bytes"))

    if not headers.check_header(header, "Connection"):
        if connection:
            default_header.append(("Connection", "keep-alive"))
        else: 
            default_header.append(("Connection", "close"))
            
    if type(content) == list or type(content) == dict:
        content = json.dumps(content)

    if type(content) == str:
        content = content.encode()

    return headers.encode(status, header + default_header) + content
       
def response_handle(response, request):
    connection = "header" in request and "Connection" in request["header"] and request["header"]["Connection"] == "keep-alive"
    if type(response) == str or type(response) == bytes or type(response) == list or type(response) == dict:
        request["conn"].sendall(encode_response(response, connection=connection))
        return connection
    
    elif type(response) == bool:
        return response
    
    elif type(response) == Response:
        if type(response.content) == str or type(response.content) == bytes or type(response.content) == list or type(response.content) == dict:
            request["conn"].sendall(encode_response(response.content, response.status, response.header, connection=(response.connection and connection)))
            return response.connection and connection
        
        return False
    
    elif type(response) == RawResponse:
        request["conn"].sendall(response.response)
        return response.connection and connection

    elif type(response) == Route:
        request["path"] = response.path
        request["conn"].sendall(request_handle(request).response)
        return response.connection and connection
    
    elif type(response) == Redirect:
        request["conn"].sendall(encode_response("", response.status, response.header + [("Location", response.url), ("Content-Length", "")], connection=(response.connection and connection)))
        return response.connection and connection
    
    elif type(response) == Error:
        return response_handle(errors.generate_error_message(response.error, request), request)
    
    else:
        return False
