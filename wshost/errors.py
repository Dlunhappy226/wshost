from wshost import responses
from wshost import status
import traceback


def generate_error_message(error, request):
    if error in request["config"].error_route:
        try:
            if callable(request["config"].error_route[error]):
                response = request["config"].error_route[error](request)
            else:
                response = request["config"].error_route[error]

            if type(response) == responses.Error and response.error == error:
                return create_error_message(error, request)
            
            return response

        except:
            if request["config"].debug:
                traceback.print_exc()
            return create_error_message(status.INTERNAL_SERVER_ERROR, request)

    return create_error_message(error, request)

def create_error_message(error, request):
    if error in [status.BAD_REQUEST, status.CONTENT_TOO_LARGE, status.REQUEST_HEADER_FIELDS_TOO_LARGE]:
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
