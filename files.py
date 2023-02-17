import headers
import config
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

def handleRequest(header):
    
    file = header[1].split("/")
    filename = filename = file[-1]
    try:
        if filename == "":
            content = read(config.root_directory + header[1] + "index.html")
            status = "200 OK"
            filenameType = "html"
        elif os.path.exists(config.root_directory + header[1] + "/"):
            content = ""
            status = "307 Temporary Redirect"
        else:
            content = read(config.root_directory + header[1])
            status = "200 OK"
            filenameExtension = filename.split(".")
            if filenameExtension[-1] in fileType:
                filenameType = filenameExtension[-1]
            else:
                filenameType = "txt"

    except:
        content = read(config.root_directory + "/404.html")
        status = "404 Not Found"
        filenameType = "html"
    
    if status == "307 Temporary Redirect":
        response = headers.encode(status, [("Location", header[1] + "/")]).encode()
    else:
        type = fileType[filenameType]
        if type[1]:
            response = headers.encode(status, [
                ("Content-Length", str(len(content))),
                ("Content-Type", type[0]),
                ("accept-ranges", "bytes")
            ]).encode() + content
        else:
            response = headers.encode(status, [(
                "Content-Length", str(len(content))),
                ("Content-Type", type[0])
            ]).encode() + content
    return response