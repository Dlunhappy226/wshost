from wshost import headers


def get_cookie(request):
    if "Cookie" not in request["header"]:
        return []
    
    return headers.header_decode(request["header"]["Cookie"])
