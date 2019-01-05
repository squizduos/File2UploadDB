import json

from django.http import Http404
from django.core.exceptions import PermissionDenied

from rest_framework.views import exception_handler

exception_definitions = {
    403: {'error': 'Forbidden access to route or object'},
    404: {'error': 'Object not found'}
}


def get_exception_definition(status_code):
    return json.dumps(exception_definitions[status_code])


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, PermissionDenied):  
        custom_response_data = exception_definitions[403]
        response.data = custom_response_data
    if isinstance(exc, Http404):  
        custom_response_data = exception_definitions[404]
        response.data = custom_response_data
    return response
