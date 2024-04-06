from urllib.parse import unquote_plus as parse_form
from urllib.parse import unquote as parse_url
from wshost import exceptions
from wshost import headers
import urllib.parse


def form_decode(request):
    fields = request["body"].decode().split("&")
    form = {}
    for x in fields:
        field, sep, value = x.partition("=")
        if not sep:
            raise exceptions.BadRequest

        form[urllib.parse.unquote_plus(field)] = urllib.parse.unquote_plus(value)

    return form

def content_decode(content):
    header, sep, body = content.partition(b"\r\n\r\n")
    if not sep:
        raise exceptions.BadRequest
    
    fields = header.decode().split("\r\n")
    headers = {}
    for x in fields:
        field, sep, value = x.partition(":")
        if not sep:
            raise exceptions.BadRequest
        
        headers[field] = value.lstrip()

    return headers, body

def multipart_decode(request):
    boundary = headers.header_decode(request["header"]["Content-Type"])["boundary"]
    fields = request["body"].split(f"--{boundary}".encode())
    fields.pop(0)
    if fields.pop() != b"--\r\n":
        raise exceptions.BadRequest
    
    form_content = {}

    for x in fields:
        header, content_body = content_decode(x[2:-2])
        disposition = headers.header_decode_quote(header["Content-Disposition"])

        if "filename" in disposition:
            header["filename"] = disposition["filename"].strip('"')

        name = disposition["name"].strip('"')

        if name in form_content:
            form_content[name].append((header, content_body))

        else:
            form_content[name] = [(header, content_body)]
        
    return form_content
