from wshost import contents
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
REQUEST_HEADER_FIELDS_TOO_LARGE = "431 Request Header Fields Too Large"

INTERNAL_SERVER_ERROR = "500 Internal Server Error"
SERVICE_UNAVAILABLE = "503 Service Unavailable"


def encode(status=OK, content=[]):
    utctime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    header_content = {}
    header_content["Server"] = "WSHost/1.0"
    header_content["Date"] = utctime
    header = "HTTP/1.1 {}\r\n".format(status) 

    for key in header_content:
        header = header + "{}: {}\r\n".format(key, header_content[key])

    for key in content:
        header = header + "{}: {}\r\n".format(key[0], key[1])

    header = header + "\r\n"
    return header

def decode(request):
    header, sep, body = request.partition(b"\r\n\r\n")
    content = header.decode().split("\r\n")
    head = content.pop(0)
    header_dist = {}
    for key in content:
        header_key, sep, header_con = key.partition(":")
        header_dist[header_key.strip()] = header_con.strip()

    return head, header_dist, body

def head_decode(head):
    method, path, protocol = head.split(" ")
    return method, path, protocol

def path_decode(path):
    path, sep, parameter = path.partition("?")
    parameters = contents.decode(parameter, "&")

    return urllib.parse.unquote(path), parameters
    