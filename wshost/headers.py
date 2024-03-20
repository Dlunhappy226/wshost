import urllib.parse
import time


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
PAYLOAD_TOO_LARGE = "413 Payload Too Large"
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
        utctime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        default_headers["Date"] = utctime
        
    header = "HTTP/1.1 {}\r\n".format(status) 

    for field in default_headers:
        header += f"{field}: {default_headers[field]}\r\n"

    for field in headers:
        header += f"{field[0]}: {field[1]}\r\n"

    header += "\r\n"
    return header

def decode(request):
    header, sep, body = request.partition(b"\r\n\r\n")
    fields = header.decode().split("\r\n")
    head = fields.pop(0)
    headers = {}
    for x in fields:
        field, sep, value = x.partition(":")
        headers[field] = value.lstrip()

    return head, headers, body

def head_decode(head):
    method, path, protocol = head.split(" ")
    return method, path, protocol

def path_decode(path):
    path, sep, raw_parameter = path.partition("?")

    fields = raw_parameter.split("&")
    parameters = {}
    for x in fields:
        field, sep, value = x.partition("=")
        parameters[urllib.parse.unquote(field)] = urllib.parse.unquote(value)

    return urllib.parse.unquote(path), parameters

def header_decode(header):
    headers = header.split("; ")
    fields = {}
    for x in headers:
        field, sep, value = x.partition("=")
        fields[field] = value

    return fields
    