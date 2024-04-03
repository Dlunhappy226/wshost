from wshost import headers
import urllib.parse


def get_cookie(request):
    if "Cookie" not in request["header"]:
        return {}
    
    return headers.header_decode(request["header"]["Cookie"])

def set_cookie(name, value, option=""):
    if not option:
        return ("Set-Cookie", f"{name}={urllib.parse.quote(value)}")
    else:
        return ("Set-Cookie", f"{name}={urllib.parse.quote(value)}; {option}")
    