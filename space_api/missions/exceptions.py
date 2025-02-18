from http.client import responses

from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "error": {
                "code": response.status_code,
                "message": response.data.get("detail", "An error occured"),
                "errors": response.data
            }
        }

    return response
