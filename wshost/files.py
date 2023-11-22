import wshost.headers as headers
import mimetypes
import os


def read(filename):
    file = open(filename, "rb")
    content = file.read()
    file.close()
    return content

def handle_request(method, path, root, error_html):
    file = path.split("/")
    filename = file[-1]
    method = method.lower()
    
    if method == "get" or method == "post" or method == "head":
        try:
            if filename == "":
                content = read(root + path + "index.html")
                status = headers.OK
                content_type = "text/html"

            elif os.path.exists(root + path + "/"):
                content = b""
                status = "307 Temporary Redirect"
                response = headers.encode(status, [("Location", path + "/")]).encode()
                content_type = ""

            else:
                content = read(root + path)
                status = headers.OK
                content_type = mimetypes.guess_type(filename)[0]
                if content_type == None:
                    content_type = "text/plain"

        except:
            content = error_html.format(headers.NOT_FOUND, headers.NOT_FOUND).encode()
            status = headers.NOT_FOUND
            content_type = "text/html"
        
        content_length = str(len(content))

        if method == "head":
            content = b""

        if content_type != "":
            try:
                content.decode()
                header = [
                    ("Content-Type", content_type),
                    ("Content-Length", content_length),
                    ("Connection", "keep-alive")
                ]
            except UnicodeDecodeError:
                header = [
                    ("Content-Type", content_type),
                    ("Content-Length", content_length),
                    ("Accept-Ranges", "bytes"),
                    ("Connection", "keep-alive")
                ]
        else:
            header = [
                ("Connection", "keep-alive")
            ]
        
        response = headers.encode(status, header).encode() + content
    else:
        response = generate_error_message(headers.METHOD_NOT_ALLOWED, error_html)

    return response

def generate_error_message(error, error_html):
    if error != headers.BAD_REQUEST:
        connection = "keep-alive"
    else:
        connection = "close"
    error_message = error_html.format(error, error).encode()
    response = headers.encode(headers.METHOD_NOT_ALLOWED, [
        ("Content-Length", len(error_message)),
        ("Content-Type", "text/html"),
        ("Connection", connection)
    ]).encode() + error_message

    return response

def encode_response(content, status=headers.OK):
    return headers.encode(status, [
        ("Content-Length", len(content))
    ]).encode() + content.encode()
