import wshost.headers as headers
import os

fileType = {
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

def handleRequest(header, root):
    
    file = header[1].split("/")
    filename = filename = file[-1]
    try:
        if filename == "":
            content = read(root + header[1] + "index.html")
            status = "200 OK"
            filenameType = "html"
        elif os.path.exists(root + header[1] + "/"):
            content = ""
            status = "307 Temporary Redirect"
        else:
            content = read(root + header[1])
            status = "200 OK"
            filenameExtension = filename.split(".")
            if filenameExtension[-1] in fileType:
                filenameType = filenameExtension[-1]
            else:
                filenameType = "txt"

    except:
        content = read(root + "/404.html")
        status = "404 Not Found"
        filenameType = "html"
    
    if header[0] == "GET" or header[0] == "POST" or header[0] == "HEAD":
        if status == "307 Temporary Redirect":
            response = headers.encode(status, [("Location", header[1] + "/")]).encode()
        else:
            contentLength = str(len(content))
            if header[0] == "HEAD":
                content = b""
            type = fileType[filenameType]
            if type[1]:
                response = headers.encode(status, [
                    ("Content-Length", contentLength),
                    ("Content-Type", type[0]),
                    ("Accept-Ranges", "bytes")
                ]).encode() + content
            else:
                response = headers.encode(status, [
                    ("Content-Length", contentLength),
                    ("Content-Type", type[0])
                ]).encode() + content
    else:
        response = headers.encode("405 Method Not Allowed", [
            ("Content-Length", "167"),
            ("Content-Type", "text/html"),
        ]).encode() + read(root + "/405.html")

    return response