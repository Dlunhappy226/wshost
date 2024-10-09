from wshost import exceptions
from base64 import b64decode


def get_auth(request):
    if "Authorization" in request["header"]:
        auth_type, _, auth_key = request["header"]["Authorization"].partition(" ")
        if not auth_key:
            raise exceptions.BadRequest
        
        if auth_type == "Basic":
            basic_cert = b64decode(auth_key).decode()
            user, _, password = basic_cert.partition(":")
            if not password:
                raise exceptions.BadRequest
            
            return user, password
                      
    return "", ""
