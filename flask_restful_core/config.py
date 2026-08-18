import os
from dotenv import load_dotenv

load_dotenv()


class DefaultConfig:
    env_name = 'DEFAULT'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///develop.db')

    # LOGGING
    # LOG_DESTINATION: 'stdout' (default, best for containers/log-shipping agents), 'file', or 'both'.
    LOG_DESTINATION = os.environ.get('LOG_DESTINATION', 'stdout')
    LOG_DIR = os.environ.get('LOG_DIR', './log')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')


class Development(DefaultConfig):
    env_name = 'DEVELOP'


class Test(DefaultConfig):
    env_name = 'TEST'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///test.db')


class Production(DefaultConfig):
    env_name = 'PRODUCTION'
