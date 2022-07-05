# -*- coding: utf-8 -*-

"""Background jobs."""

import atexit
from datetime import timezone

from apscheduler.schedulers.background import BackgroundScheduler

from smartrade import app_logger

logger = app_logger.get_logger(__name__)

def _retrieve_quotes(app):
    logger.debug("Retrieving quotes")
    from smartrade.Inspector import Inspector
    for account in app.config['broker_client'][0]['accounts']:
        acct_id = list(account.values())[0]
        db_name = app.config['DATABASE']
        Inspector(db_name, acct_id).summarize()

def run(app):
    hour = '20-23'
    minute = '30' if app.config['ENV'] == 'production' else '45'
    logger.debug(f"Scheduling jobs on HH({hour}):MM({minute}) every weekday")
    scheduler = BackgroundScheduler(timezone=timezone.utc)
    scheduler.add_job(func=lambda: _retrieve_quotes(app), trigger="cron",
                      day_of_week='mon-fri', hour=hour, minute=minute)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
