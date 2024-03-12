from urllib.parse import unquote_plus as parse_form
from urllib.parse import unquote as parse_url


def header_decode(header):
    headers = header.split("; ")
    fields = {}
    for x in headers:
        field, sep, value = x.partition("=")
        fields[field] = value

    return fields

def form_decode(body):
    fields = body.decode().split("&")
    form = {}
    for x in fields:
        field, sep, value = x.partition("=")
        form[parse_form(field)] = parse_form(value)

    return form

def content_decode(content):
    header, sep, body = content.partition(b"\r\n\r\n")
    fields = header.decode().split("\r\n")
    headers = {}
    for x in fields:
        field, sep, value = x.partition(":")
        headers[field] = value.lstrip()

    return headers, body

def multipart_decode(request, body):
    boundary = header_decode(request["header"]["Content-Type"])["boundary"]
    body, sep, end = body.partition(f"\r\n--{boundary}--".encode())
    fields = body.split(f"--{boundary}\r\n".encode())
    fields.pop(0)
    form_content = []
    for x in fields:
        header, content_body = content_decode(x)
        form_content.append((header, content_body))
        
    return form_content

def get_cookie(request):
    if "Cookie" not in request["header"]:
        return []
    
    return header_decode(request["header"]["Cookie"])
