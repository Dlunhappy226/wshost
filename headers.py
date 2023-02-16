import time

def encode(status, content):
    utctime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    headerContent = {}
    headerContent["Date"] = utctime
    headerContent["Server"] = "WSHost/1.0"

    header = "HTTP/1.1 {}\r\n".format(status) 

    for key in headerContent:
        header = header + "{}: {}\r\n".format(key, headerContent[key])

    for key in content:
        header = header + "{}: {}\r\n".format(key[0], key[1])

    return header + "\r\n"