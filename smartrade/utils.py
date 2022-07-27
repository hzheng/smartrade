# -*- coding: utf-8 -*-

from collections.abc import Iterable
from enum import Enum
import datetime
import os

from dateutil.relativedelta import relativedelta
import pymongo

from smartrade.exceptions import BadRequestError, TooManyRequestsError

ASC = pymongo.ASCENDING
DESC = pymongo.DESCENDING

def get_database(db_name):
    client = pymongo.MongoClient(os.environ.get('MONGODB_URI', "mongodb://127.0.0.1:27017"))
    return client[db_name]

def check(assertion, error_message, log=None, throw_error=True):
    if assertion: return

    if log:
        log(error_message)
    if throw_error:
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

def to_json(obj):
    if callable(getattr(obj, "to_json", None)): return obj.to_json()

    if isinstance(obj, Iterable) and not isinstance(obj, str):
        return [to_json(item) for item in obj]

    if not hasattr(obj, '__dict__'): return obj

    clazz = obj.__class__
    return {prop: to_json(getattr(obj, prop)) for prop in dir(clazz)
            if isinstance(getattr(clazz, prop), property)}

def parse_date_range(date_range):
    start_date = end_date = None
    today = datetime.datetime.today()
    diff = int(date_range[1:])
    if date_range.startswith("w"):
        start_date = today - datetime.timedelta(days=today.weekday())
        if diff < 0:
            start_date += relativedelta(weeks=diff)
            end_date = start_date + datetime.timedelta(days=6)
    elif date_range.startswith("m"):
        start_date = today.replace(day=1)
        if diff != 0:
            start_date += relativedelta(months=diff)
            end_date = start_date + relativedelta(day=31)
    elif date_range.startswith("y"):
        start_date = today.replace(month=1, day=1)
        if diff != 0:
            start_date += relativedelta(years=diff)
            end_date = start_date.replace(month=12, day=31)
    return start_date, end_date

if __name__ == '__main__':
    print("w-0", parse_date_range("w-0"))
    print("w-1", parse_date_range("w-1"))
    print("w-2", parse_date_range("w-2"))
    print("m-0", parse_date_range("m-0"))
    print("m-1", parse_date_range("m-1"))
    print("m-2", parse_date_range("m-2"))
    print("y-0", parse_date_range("y-0"))
    print("y-1", parse_date_range("y-1"))
    print("y-2", parse_date_range("y-2"))