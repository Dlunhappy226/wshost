from wshost import responses
from wshost import headers
import base64


def unauthorized(realm="Acess to the staging site."):
    responses.Response("", status=headers.UNAUTHORIZED, header=[("WWW-Authenticate", f"Basic realm={realm}")])

def get_auth(request):
    if "Authorization" in request["header"]:
        auth_type, sep, auth_key = request["header"]["Authorization"].partition(" ")
        if auth_type == "Basic":
            user, sep, password = base64.b64decode(auth_key).decode().partition(":")
            return user, password
                      
    return "", ""
