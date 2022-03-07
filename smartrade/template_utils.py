# -*- coding: utf-8 -*-

import datetime

from smartrade import app

@app.context_processor
def today():
    return {'today': datetime.date.today()}

@app.template_filter('first_week_day')
def first_week_day(date):
    return date - datetime.timedelta(days=date.weekday())

@app.context_processor
def last_week_first_day():
    date = datetime.date.today()
    return {'last_week_first_day' : date - datetime.timedelta(days=date.weekday()+7) }

@app.context_processor
def last_week_last_day():
    date = datetime.date.today()
    return {'last_week_last_day' : date - datetime.timedelta(days=date.weekday()+1) }

@app.template_filter('first_month_day')
def first_month_day(date):
    return date.replace(day=1)

@app.context_processor
def last_month_first_day():
    last_month_last_day = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
    return {'last_month_first_day': last_month_last_day.replace(day=1)}

@app.context_processor
def last_month_last_day():
    return {'last_month_last_day': datetime.date.today().replace(day=1) - datetime.timedelta(days=1)}

@app.context_processor
def last_year():
    return {'last_year': datetime.date.today() - datetime.timedelta(days=365)}

@app.template_filter('first_year_day')
def first_year_day(date):
    return date.replace(month=1, day=1)

@app.template_filter('last_year_day')
def last_year_day(date):
    return date.replace(month=12, day=31)

@app.template_filter('ui')
def ui(symbol):
    return symbol.split("_")[0]
