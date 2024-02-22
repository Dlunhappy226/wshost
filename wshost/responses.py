from wshost import headers
import mimetypes
import os


class response:
    def __init__(self, status, headers, content):
        self.status = status
        self.headers = headers
        self.content = content


class raw_response:
    def __init__(self, response):
        self.response = response


class redirect:
    def __init__(self, url, status=headers.TEMPORARY_REDIRECT):
        self.url = url
        self.status = status


class route:
    def __init__(self, path):
        self.path = path
    
    def route(self, request):
        request["path"] = self.path
        return handle_request(request)


def read(filename):
    file = open(filename, "rb")
    content = file.read()
    file.close()
    return content

def handle_request(request):
    method = request["method"].lower()
    path = request["path"]
    root = request["config"].root_directory
    error_html = request["config"].error_html
    file = path.split("/")
    filename = file[-1]
    
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

    request["conn"].sendall(response)
    
    return True

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

def encode_response(content, status=headers.OK, header=[]):
    return headers.encode(status, header + [
        ("Content-Length", len(content)),
        ("Connection", "keep-alive")
    ]).encode() + content.encode()

def encode_binary_response(content, status=headers.OK, header=[]):
    return headers.encode(status, header + [
        ("Content-Length", len(content)),
        ("Accept-Ranges", "bytes"),
        ("Connection", "keep-alive")
    ]).encode() + content
