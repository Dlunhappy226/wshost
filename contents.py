def decode(content, separator):
    splited = content.split(separator)
    decoded = []
    for x in splited:
        key, sep, value = x.partition("=")
        decoded.append((key.strip(), value.strip()))
    return decoded

def header_decode(content):
    return decode(content, ";")

def content_decode(content):
    header, sep, body = content.partition(b"\r\n\r\n")
    headerContent = header.decode().split("\r\n")
    headerDist = {}
    for key in headerContent:
        headerKey, sep, headerCon = key.partition(":")
        headerDist[headerKey.strip()] = headerCon.strip()
    return headerDist, body

def form_decode(content):
    return decode(content, "&")