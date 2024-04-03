from wshost import responses
from wshost import statuses
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
            return create_error_message(statuses.INTERNAL_SERVER_ERROR, request)

    return create_error_message(error, request)

def create_error_message(error, request):
    error_html = request["config"].error_html
    error_message = error_html.format(error, error)
    connection = error not in [statuses.BAD_REQUEST, statuses.CONTENT_TOO_LARGE, statuses.REQUEST_HEADER_FIELDS_TOO_LARGE]

    return responses.Response(error_message, status=error, connection=connection, content_type="text/html")
