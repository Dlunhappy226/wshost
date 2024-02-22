def decode(content, separator):
    splited = content.split(separator)
    decoded = {}
    for x in splited:
        key, sep, value = x.partition("=")
        decoded[key.strip()] = value.strip()

    return decoded

def header_decode(header):
    splited = header.split(";")
    decoded = {}
    for x in splited:
        key, sep, value = x.partition("=")
        decoded[key.strip()] = value.strip(' " ')

    return decoded

def content_decode(content):
    header, sep, body = content.partition(b"\r\n\r\n")
    header_content = header.decode().split("\r\n")
    header_dist = {}
    for key in header_content:
        header_key, sep, header_con = key.partition(":")
        header_dist[header_key.strip()] = header_con.strip()

    return header_dist, body

def form_decode(content):
    return decode(content, "&")

def multiform_decode(boundary, body):
    body, sep, end = body.partition(("\r\n--" + boundary + "--").encode())
    content = body.split(("--" + boundary + "\r\n").encode())
    content.pop(0)
    form_content = []
    for x in content:
        header, content_body = content_decode(x)
        form_content.append((header, content_body))
        
    return form_content

def get_cookie(request):
    if "Cookie" not in request["header"]:
        return False
    
    return header_decode(request["header"]["Cookie"])

def get_data(request, max_size=65536):
    if request["body"]:
        return(request["body"])
    else:
        return(request["conn"].recv(max_size))
