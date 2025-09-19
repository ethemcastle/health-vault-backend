import logging

from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def base_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    logger.exception(exc, exc_info=True)
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response
