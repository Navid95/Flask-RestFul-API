import json
import logging
import os
import sys

from flask_restful_core.utilities.logging import APP_LOGGER_NAME
from flask_restful_core.utilities.logging import API_LOGGER_NAME


class JsonFormatter(logging.Formatter):
    """
    Formats log records as JSON lines.

    Handles dict messages (as used throughout this package) by merging their keys directly into the
    payload instead of relying on logging's default str(record.msg) stringification, which would produce
    a Python repr rather than valid JSON.
    """

    def format(self, record):
        payload = {
            'loggername': record.name,
            'levelname': record.levelname,
            'datetime': self.formatTime(record),
        }
        if isinstance(record.msg, dict):
            payload.update(record.msg)
        else:
            payload['message'] = record.getMessage()
        if record.exc_info:
            payload['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(app):
    """
    Configure the app_logger/api_logger loggers based on the Flask app's config.

    Called explicitly from create_app() (rather than as an import-time side effect) so that logging
    behaviour reflects the consuming app's actual config (env vars, custom Config subclasses) instead of
    whatever happened to be importable at module-import time.

    Config keys read from app.config:
    - LOG_DESTINATION: 'stdout' (default), 'file', or 'both'.
    - LOG_DIR: directory for file handlers, used only when LOG_DESTINATION is 'file'/'both'. Created lazily.
    - LOG_LEVEL: level name for both loggers, defaults to 'DEBUG'.
    """
    app_logger = logging.getLogger(APP_LOGGER_NAME)
    api_logger = logging.getLogger(API_LOGGER_NAME)

    # Idempotent: repeated create_app() calls (e.g. across test modules) shouldn't stack duplicate handlers.
    app_logger.handlers.clear()
    api_logger.handlers.clear()
    app_logger.propagate = False
    api_logger.propagate = False

    level = getattr(logging, str(app.config.get('LOG_LEVEL', 'DEBUG')).upper(), logging.DEBUG)
    destination = app.config.get('LOG_DESTINATION', 'stdout')
    formatter = JsonFormatter()

    if destination in ('stdout', 'both'):
        for logger in (app_logger, api_logger):
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    if destination in ('file', 'both'):
        log_dir = app.config.get('LOG_DIR', './log')
        os.makedirs(log_dir, exist_ok=True)

        app_log_file_handler = logging.FileHandler(filename=os.path.join(log_dir, 'app-log.txt'), mode='a+')
        exception_log_file_handler = logging.FileHandler(filename=os.path.join(log_dir, 'exception-log.txt'), mode='a+')
        api_log_file_handler = logging.FileHandler(filename=os.path.join(log_dir, 'api-log.txt'), mode='a+')

        exception_log_file_handler.setLevel(logging.ERROR)
        for handler in (app_log_file_handler, exception_log_file_handler, api_log_file_handler):
            handler.setFormatter(formatter)

        app_logger.addHandler(app_log_file_handler)
        app_logger.addHandler(exception_log_file_handler)
        api_logger.addHandler(api_log_file_handler)

    app_logger.setLevel(level)
    api_logger.setLevel(level)
