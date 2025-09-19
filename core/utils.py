import json
from typing import Dict

import requests

from rest_framework.response import Response
from rest_framework import status
from .serializers import ResponseSerializer, ResponseWithResultSerializer


def post_request(url: str, headers: Dict, payload: Dict) -> Dict:
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return json.loads(response.text)


def get_request(url: str, headers: Dict) -> Dict:
    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text)

def success_response(message="", result=None, status=status.HTTP_200_OK):
    if result is not None:
        return Response(
            ResponseWithResultSerializer.success(result=result, message=message),
            status=status
        )
    return Response(
        ResponseSerializer.success(message=message),
        status=status
    )

def error_response(message, errors=None, status=status.HTTP_400_BAD_REQUEST, error_type=''):
    return Response(
        ResponseSerializer.fail(message=message, errors=errors or [], error_type=error_type),
        status=status
    )


def decode_json(json_str: str) -> Dict:
    return json.loads(json_str.replace("'", '"').replace("True", "true").replace("False", "false"))