from wshost import responses
from wshost import statuses
from wshost import etags
import mimetypes
import os


def read(filename):
    file = open(filename, "rb")
    content = file.read()
    file.close()
    return content

def request_handle(request, no_etag=False):
    method = request["method"]
    path = request["path"]
    root = os.path.join(request["config"].root_directory, request["config"].html_directory).replace("\\", "/")
    file = path.split("/")
    filename = file[-1]
    
    if method in ["GET", "HEAD"]:
        try:
            if not filename:
                path = f"{path}/index.html"
                filename = "index.html"

            elif os.path.isdir(f"{root}{path}"):
                content = b""
                return responses.Redirect(f"{path}/")

            if not os.path.exists(f"{root}{path}"):
                return responses.Error(statuses.NOT_FOUND)

            content = read(f"{root}{path}")
            content_type = mimetypes.guess_type(filename)[0]

            if content_type == None:
                content_type = "text/plain"

            if not no_etag:
                last_modified = [("Last-Modified", etags.get_last_modified(f"{root}{path}"))]
                etag = etags.generate_etag(content)

                if etags.check_etag(request, etag):
                    return responses.not_modified(content, last_modified)
            
            else:
                last_modified = []
            
        except PermissionError:
            return responses.Error(statuses.NOT_FOUND)

        try:
            content = content.decode()
        except UnicodeDecodeError:
            pass

        return responses.Response(content, header=last_modified, content_type=content_type, etag=(not no_etag), no_content=(method == "head"))
    else:
        return responses.Error(statuses.METHOD_NOT_ALLOWED)
