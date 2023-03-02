def decode(content, separator):
    splited = content.split(separator)
    decoded = {}
    for x in splited:
        key, sep, value = x.partition("=")
        decoded[key.strip()] = value.strip()
    return decoded

def header_decode(content):
    splited = content.split(";")
    decoded = {}
    for x in splited:
        key, sep, value = x.partition("=")
        decoded[key.strip()] = value.strip(' " ')
    return decoded

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

def multiform_decode(boundary, body):
    body, sep, end = body.partition(("\r\n--" + boundary + "--").encode())
    content = body.split(("--" + boundary + "\r\n").encode())
    content.pop(0)
    formContent = []
    for x in content:
        header, contentBody = content_decode(x)
        formContent.append((header, contentBody))
    return formContent
