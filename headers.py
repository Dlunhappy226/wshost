from datetime import datetime, timezone
import platform

def encode(status, content):
    utctime = datetime.now(timezone.utc)
    headerContent = {}
    headerContent["Date"] = utctime.strftime("%a, %d %b %Y %H:%M:%S UTC")
    headerContent["Server"] = "WSHost/1.0 Python/" + platform.python_version()

    header = "HTTP/1.1 {}\r\n".format(status) 

    for key in headerContent:
        header = header + "{}: {}\r\n".format(key, headerContent[key])

    for key in content:
        header = header + "{}: {}\r\n".format(key[0], key[1])

    return header + "\r\n"