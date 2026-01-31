from rest_framework.views import exception_handler
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = "Request failed"

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            message = "Authentication required"
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            message = "You do not have permission to perform this action"
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            message = "Resource not found"
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            message = "Validation failed"

        response.data = {
            "success": False,
            "message": message,
            "errors": response.data,
        }

    return response
