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
        Inspector(db_name, acct_id).total_positions()

def run(app):
    logger.debug("Scheduling jobs")
    scheduler = BackgroundScheduler(timezone=timezone.utc)
    scheduler.add_job(func=lambda: _retrieve_quotes(app), trigger="cron",
                      day_of_week='mon-fri', hour='20-23', minute='30')
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
