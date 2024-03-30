from wshost import responses
from wshost import headers
import traceback


def generate_error_message(error, request):
    if error in request["config"].error_route:
        try:
            if callable(type(request["config"].error_route[error])):
                return request["config"].error_route[error](request)
            else:
                return request["config"].error_route[error]
        except:
            if request["config"].debug:
                traceback.print_exc()
            return create_error_message(headers.INTERNAL_SERVER_ERROR, request)

    return create_error_message(error, request)

def create_error_message(error, request):
    if error == headers.BAD_REQUEST or error == headers.CONTENT_TOO_LARGE or error == headers.REQUEST_HEADER_FIELDS_TOO_LARGE:
        connection = "close"
    else:
        connection = "keep-alive"

    error_html = request["config"].error_html
    error_message = error_html.format(error, error)

    return responses.Response(error_message, status=error, header=[
        ("Content-Length", len(error_message)),
        ("Content-Type", "text/html"),
        ("Connection", connection)
    ], connection=(connection == "keep-alive"))
