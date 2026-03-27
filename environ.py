import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///develop.db')

# LOGGING
APP_LOGGER_NAME = 'app_logger'
API_LOGGER_NAME = 'api_logger'
APP_LOGGER_FILE_PATH = './log/app-log.txt'
API_LOGGER_FILE_PATH = './log/api-log.txt'
EXCEPTION_LOGGER_FILE_PATH = './log/exception-log.txt'
