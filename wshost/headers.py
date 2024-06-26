from wshost import exceptions
from wshost import statuses
import urllib.parse
import time
import re


def check_header(headers, field):
    for header in headers:
        if header[0] == field:
            return True
        
    return False

def encode(status=statuses.OK, headers=[]):
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
        if field[1]:
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
        if not sep:
            raise exceptions.BadRequest
    
        headers[field] = value.lstrip()

    return headers

def first_line_decode(first_line):
    method, path, protocol = first_line.split(" ")
    protocol, sep, version = protocol.partition("/")
    if not sep:
        raise exceptions.BadRequest

    return method, path, protocol, version

def path_decode(path):
    path, sep, raw_parameter = path.partition("?")

    fields = raw_parameter.split("&")
    parameters = {}
    for x in fields:
        field, sep, value = x.partition("=")
        parameters[urllib.parse.unquote(field)] = urllib.parse.unquote(value)

    return urllib.parse.unquote(path), parameters

def header_decode(header, separator=False):
    headers = header.split(";")
    fields = {}
    for x in headers:
        field, sep, value = x.partition("=")
        if separator and not sep:
            raise exceptions.BadRequest
        
        fields[field] = value

    return fields

def header_decode_quote(header, separator=False):
    headers = re.split(r"; (?=(?:[^\"]*[\"][^\"]*[\"])*[^\"]*$)", header)
    fields = {}
    for x in headers:
        field, sep, value = x.partition("=")
        if separator and not sep:
            raise exceptions.BadRequest

        fields[field] = value

    return fields

def encode_time(time_code):
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time_code)
    