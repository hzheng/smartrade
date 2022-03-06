import logging
import sys
from logging.handlers import TimedRotatingFileHandler


class Logger():

    FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def __init__(self, log_file, log_level=logging.DEBUG):
        self._log_file = log_file
        self._log_level = log_level

    def _get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.FORMATTER)
        return console_handler

    def _get_file_handler(self):
        file_handler = TimedRotatingFileHandler(self._log_file, when='midnight')
        file_handler.setFormatter(self.FORMATTER)
        return file_handler

    def get_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        logger.setLevel(self._log_level)

        logger.addHandler(self._get_console_handler())
        logger.addHandler(self._get_file_handler())

        logger.propagate = False
        return logger
