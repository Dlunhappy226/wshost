from wshost import responses
from wshost import status
import base64


def unauthorized(realm="Acess to the staging site."):
    return responses.Response("", status=status.UNAUTHORIZED, header=[("WWW-Authenticate", f"Basic realm={realm}")])

def get_auth(request):
    if "Authorization" in request["header"]:
        auth_type, sep, auth_key = request["header"]["Authorization"].partition(" ")
        if auth_type == "Basic":
            user, sep, password = base64.b64decode(auth_key).decode().partition(":")
            return user, password
                      
    return "", ""
