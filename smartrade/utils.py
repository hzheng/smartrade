# -*- coding: utf-8 -*-

import os

import pymongo

from smartrade.exceptions import BadRequestError, TooManyRequestsError

ASC = pymongo.ASCENDING
DESC = pymongo.DESCENDING

def get_database(db_name):
    client = pymongo.MongoClient(os.environ.get('MONGODB_URI', "mongodb://127.0.0.1:27017"))
    return client[db_name]

def check(assertion, error_message, logger=None):
    if assertion: return

    if logger:
        logger.error(error_message)
    raise AssertionError(error_message)
    
def http_response(response):
    code = response.status_code
    if code == 400:
        raise BadRequestError()
 
    if code == 429:
        raise TooManyRequestsError()

    check(code == 200, response.raise_for_status())
    return response.json()

def get_value(obj, *attrs):
    for attr in attrs:
        if attr in obj:
            return obj[attr]
    return None