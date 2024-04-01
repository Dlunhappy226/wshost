from wshost import exceptions
import urllib.parse
import time
import re


SWITCHING_PROTOCOLS = "101 Switching Protocols"

OK = "200 OK"
NO_CONTENT = "204 No Content"

MOVED_PERMANENTLY = "301 Moved Permanently"
FOUND = "302 Found"
NOT_MODIFIED = "304 Not Modified"

BAD_REQUEST = "400 Bad Request"
UNAUTHORIZED = "401 Unauthorized"
FORBIDDEN = "403 Forbidden"
NOT_FOUND = "404 Not Found"
METHOD_NOT_ALLOWED = "405 Method Not Allowed"
GONE = "410 Gone"
CONTENT_TOO_LARGE = "413 Content Too Large"
URI_TOO_LARGE = "414 URI Too Long"
REQUEST_HEADER_FIELDS_TOO_LARGE = "431 Request Header Fields Too Large"

INTERNAL_SERVER_ERROR = "500 Internal Server Error"
SERVICE_UNAVAILABLE = "503 Service Unavailable"

def check_header(headers, field):
    for header in headers:
        if header[0] == field:
            return True
        
    return False

def encode(status=OK, headers=[]):
    default_headers = {}
    if not check_header(headers, "Server"):
        default_headers["Server"] = "wshost"

    if not check_header(headers, "Date"):
        utctime = encode_time(time.gmtime())
        default_headers["Date"] = utctime
        
    header = "HTTP/1.1 {}\r\n".format(status) 

    for field in default_headers:
        header += f"{field}: {default_headers[field]}\r\n"

    for field in headers:
        if field[1] != "":
            header += f"{field[0]}: {field[1]}\r\n"

    header += "\r\n"
    return header.encode()

def decode(header):
    fields = header.decode().split("\r\n")
    fields.pop()
    headers = {}
    for x in fields:
        if ":" not in x:
            raise exceptions.BadRequest
        
        field, sep, value = x.partition(":")
        headers[field] = value.lstrip()

    return headers

def first_line_decode(first_line):
    method, path, protocol = first_line.split(" ")
    protocol, sep, version = protocol.partition("/")
    return method, path, protocol, version

def path_decode(path):
    path, sep, raw_parameter = path.partition("?")

    fields = raw_parameter.split("&")
    parameters = {}
    for x in fields:
        field, sep, value = x.partition("=")
        parameters[urllib.parse.unquote(field)] = urllib.parse.unquote(value)

    return urllib.parse.unquote(path), parameters

def header_decode(header):
    headers = re.split(r"; (?=(?:[^\"]*[\"][^\"]*[\"])*[^\"]*$)", header)
    fields = {}
    for x in headers:
        field, sep, value = x.partition("=")
        fields[field] = value

    return fields

def encode_time(time_code):
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time_code)
    