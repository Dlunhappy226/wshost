from wshost import exceptions
import base64


def get_auth(request):
    if "Authorization" in request["header"]:
        auth_type, sep, auth_key = request["header"]["Authorization"].partition(" ")
        if not sep:
            raise exceptions.BadRequest
        
        if auth_type == "Basic":
            user, sep, password = base64.b64decode(auth_key).decode().partition(":")
            if not sep:
                raise exceptions.BadRequest
            
            return user, password
                      
    return "", ""
