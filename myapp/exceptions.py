from rest_framework import status
from rest_framework.exceptions import APIException


class AlreadyExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Instance already exists.'
    default_code = 'already_exists'


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Request conflicts with the current user profile of the server.'
    default_code = 'conflict'


