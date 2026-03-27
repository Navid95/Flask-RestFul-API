import logging
from logging import FileHandler
from environ import APP_LOGGER_NAME
from environ import API_LOGGER_NAME
from environ import APP_LOGGER_FILE_PATH
from environ import API_LOGGER_FILE_PATH
from environ import EXCEPTION_LOGGER_FILE_PATH

# Handlers
app_log_file_handler = FileHandler(filename=APP_LOGGER_FILE_PATH, mode='a+')
api_log_file_handler = FileHandler(filename=API_LOGGER_FILE_PATH, mode='a+')
exception_log_file_handler = FileHandler(filename=EXCEPTION_LOGGER_FILE_PATH, mode='a+')

# Formats
json_file_format = {
    'loggername': '%(name)s',
    'levelname': '%(levelname)s',
    'datetime': '%(asctime)s',
    'message': '%(message)s'
}

json_api_format = {
    'datetime': '%(asctime)s',
    'message': '%(message)s'
}

json_formatter = logging.Formatter(
    fmt='{"loggername": "%(name)s", "levelname": "%(levelname)s", "datetime": "%(asctime)s", "message": "%(message)s"}'
)
json_formatter_api = logging.Formatter(
    fmt='{"datetime": "%(asctime)s", "message": "%(message)s"}'
)


# configuration
exception_log_file_handler.setLevel(logging.ERROR)
exception_log_file_handler.setFormatter(json_formatter)

app_log_file_handler.setLevel(logging.DEBUG)
app_log_file_handler.setFormatter(json_formatter)

api_log_file_handler.setFormatter(json_formatter_api)
api_log_file_handler.setLevel(logging.INFO)

# Loggers
app_logger = logging.getLogger(APP_LOGGER_NAME)
api_logger = logging.getLogger(API_LOGGER_NAME)

app_logger.addHandler(app_log_file_handler)
app_logger.addHandler(exception_log_file_handler)
app_logger.setLevel(logging.DEBUG)

api_logger.addHandler(api_log_file_handler)
api_logger.setLevel(logging.DEBUG)
