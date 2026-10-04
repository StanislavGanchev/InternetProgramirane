"""Uniform error format for every API endpoint.

Every error response has the shape:

    {"errors": {"<field or detail>": ["message", ...]}}
"""

from rest_framework.views import exception_handler


def _as_list(value):
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return [str(value)]


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    data = response.data
    if isinstance(data, dict):
        if set(data.keys()) == {"detail"}:
            errors = {"detail": _as_list(data["detail"])}
        else:
            errors = {key: _as_list(value) for key, value in data.items()}
    else:
        errors = {"non_field_errors": _as_list(data)}

    response.data = {"errors": errors}
    return response
