import headers
import config
import os

fileType = {
    "css": "text/css",
    "html": "text/html",
    "js": "text/javascript",
    "apng": "image/apng",
    "avif": "image/avif",
    "gif": "image/gif",
    "jpg": "image/jpeg",
    "png": "image/png",
    "svg": "image/svg+xml",
    "webp": "image/webp",
    "wav": "audio/wave",
    "webm": "video/webm",
    "ogg": "video/ogg",
    "mp4": "video/mp4",
    "mp3": "audio/mpeg",
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
            filenameType = fileType["html"]
        elif os.path.exists(config.root_directory + header[1] + "/"):
            content = ""
            status = "307 Temporary Redirect"
        else:
            content = read(config.root_directory + header[1])
            status = "200 OK"
            filenameExtension = filename.split(".")
            if filenameExtension[-1] in fileType:
                filenameType = fileType[filenameExtension[-1]]
            else:
                filenameType = "text/plain"

    except:
        content = read(config.root_directory + "/404.html")
        status = "404 Not Found"
        filenameType = fileType["html"]
    
    if status == "307 Temporary Redirect":
        response = headers.encode(status, [("Location", header[1] + "/")]).encode()
    else:
        response = headers.encode(status, [("Content-Length", str(len(content))), ("Content-Type", filenameType)]).encode() + content
    return response