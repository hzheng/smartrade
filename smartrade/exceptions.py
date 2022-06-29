# -*- coding: utf-8 -*-


class ClientError(Exception):
    """Client-side error"""


class ConfigurationError(ClientError):
    """Configuration error"""

class ParameterError(ClientError):
    """Parameter error"""

class BadRequestError(ClientError):
    """Bad request error"""

class TooManyRequestsError(ClientError):
    """Too many requests error"""
