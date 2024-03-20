import hashlib


def generate_etag(content):
    return f'"{hashlib.md5(content).hexdigest()}"'

def check_etag(request, etag):
    if "If-None-Match" in request["header"]:
        if request["header"]["If-None-Match"] == etag:
            return True
              
    return False
