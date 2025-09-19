from django.db import models

# Responses
DATA = 'data'
ERRORS = 'errors'
VALID = 'valid'
MESSAGE = 'message'
IS_SUCCESS = 'is_success'
FILTER_PREFIX = 'flt_'
ERROR_TYPE = 'type'
RESULT = 'result'

VALIDATION_ERROR = 'ValidationError'
HTTP_400 = 'Http400'
HTTP_404 = 'Http404'
INTEGRITY_ERROR = 'IntegrityError'
OTHER = 'Other'
FIELD_ERROR = 'FieldError'
INVALID_DATA = 'InvalidData'
UNAUTHORIZED = 'Unauthorized'
EMAIL_ERROR = 'EmailError'

DEFAULT_COUNTRY_ID = 1


class CallbackStatus(models.TextChoices):
    TRACKER = 'TRACKER', 'TRACKER'
    PAYLOAD_CALLBACK = 'PAYLOAD_CALLBACK', 'PAYLOAD_CALLBACK'
    LINK_CLICK = 'LINK_CLICK', 'LINK_CLICK'
    INTERACTION = 'INTERACTION', 'INTERACTION'
    DATA_SUBMIT = 'DATA_SUBMIT', 'DATA_SUBMIT'
