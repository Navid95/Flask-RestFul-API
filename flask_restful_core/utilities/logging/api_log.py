import logging
from datetime import datetime

from flask import g
from flask import request
from flask import Response

from flask_restful_core.utilities.logging import API_LOGGER_NAME
from flask_restful_core.utilities.logging import APP_LOGGER_NAME

app_logger = logging.getLogger(APP_LOGGER_NAME)
api_logger = logging.getLogger(API_LOGGER_NAME)


def get_request_time():
    request_time = datetime.now()
    setattr(g, 'request_time', request_time)


def log_api_call(response: Response):
    response_time = datetime.now()
    request_time = getattr(g, 'request_time')

    json_body = request.get_json(silent=True)
    body = json_body if json_body is not None else request.get_data(as_text=True)

    json_r_body = response.get_json(silent=True)
    r_body = json_r_body if json_r_body is not None else response.get_data(as_text=True)

    message = {
        'url': request.url,
        'method': request.method,
        'status_code': str(response.status_code),
        'status': response.status,
        'headers': str(request.headers),
        'body': body,
        'r_body': r_body,
        'r_headers': str(response.headers),
        'request_time': request_time.isoformat(),
        'response_time': response_time.isoformat(),
        'remote_address': request.remote_addr
    }

    api_logger.info(msg=message)
    app_logger.info(msg=message)

    return response
