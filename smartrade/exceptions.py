# -*- coding: utf-8 -*-


class ClientError(Exception):
    """Client-side error"""


class ConfigurationError(ClientError):
    """Configuration error"""

class ParameterError(ClientError):
    """Parameter error"""

class TooManyRequestsError(ClientError):
    """Parameter error"""
