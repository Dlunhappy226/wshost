import headers
import config

fileType = {
    {
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
        "mp3": "audio/mpeg"
    }
}

def read(filename):
    file = open(filename, "rb")
    content = file.read()
    file.close()
    return content

def handleRequest(header):
    try:
        content = read(config.root_directory + header[1])
        status = "200 OK"
    except FileNotFoundError:
        content = read(config.root_directory + "/404.html")
        status = "404 Not Found"
    response = headers.encode(status, [("Content-Length", str(len(content)))]).encode() + content
    return response