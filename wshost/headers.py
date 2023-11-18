import time


def encode(status, content):
    utctime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    header_content = {}
    header_content["Date"] = utctime
    header_content["Server"] = "WSHost/1.0"

    header = "HTTP/1.1 {}\r\n".format(status) 

    for key in header_content:
        header = header + "{}: {}\r\n".format(key, header_content[key])

    for key in content:
        header = header + "{}: {}\r\n".format(key[0], key[1])

    return header + "\r\n"

def decode(content):
    header, sep, body = content.partition(b"\r\n\r\n")
    header_content = header.decode().split("\r\n")
    head = header_content.pop(0)
    header_dist = {}
    for key in header_content:
        header_key, sep, header_con = key.partition(":")
        header_dist[header_key.strip()] = header_con.strip()
    return head, header_dist, body