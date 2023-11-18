import wshost.headers as headers
import os


file_type = {
    "css": ("text/css", False),
    "html": ("text/html", False),
    "js": ("text/javascript", False),
    "apng": ("image/apng", True),
    "avif": ("image/avif", True),
    "gif": ("image/gif", True),
    "jpg": ("image/jpeg", True),
    "png": ("image/png", True),
    "svg": ("image/svg+xml", False),
    "webp": ("image/webp", True),
    "wav": ("audio/wave", True),
    "webm": ("video/webm", True),
    "ogg": ("video/ogg", True),
    "mp4": ("video/mp4", True),
    "mp3": ("audio/mpeg", True),
    "txt": ("text/plain", False),
}

def read(filename):
    file = open(filename, "rb")
    content = file.read()
    file.close()
    return content

def handle_request(header, root, error_html):
    file = header[1].split("/")
    filename = file[-1]
    try:
        if filename == "":
            content = read(root + header[1] + "index.html")
            status = "200 OK"
            filename_type = "html"
        elif os.path.exists(root + header[1] + "/"):
            content = ""
            status = "200 OK"
        else:
            content = read(root + header[1])
            status = "200 OK"
            filename_extension = filename.split(".")
            if filename_extension[-1] in file_type:
                filename_type = filename_extension[-1]
            else:
                filename_type = "txt"

    except:
        content = error_html.format("404 Not Found", "404 Not Found").encode()
        status = "404 Not Found"
        filename_type = "html"
    
    if header[0] == "GET" or header[0] == "POST" or header[0] == "HEAD":
        if status == "307 Temporary Redirect":
            response = headers.encode(status, [("Location", header[1] + "/")]).encode()
        else:
            content_length = str(len(content))
            if header[0] == "HEAD":
                content = b""

            type = file_type[filename_type]
            if type[1]:
                response = headers.encode(status, [
                    ("Content-Length", content_length),
                    ("Content-Type", type[0]),
                    ("Accept-Ranges", "bytes")
                ]).encode() + content
            else:
                response = headers.encode(status, [
                    ("Content-Length", content_length),
                    ("Content-Type", type[0])
                ]).encode() + content
    else:
        error_message = error_html.format("405 Method Not Allowed", "405 Method Not Allowed").encode()
        response = headers.encode("405 Method Not Allowed", [
            ("Content-Length", len(error_message)),
            ("Content-Type", "text/html"),
        ]).encode() + error_message

    return response