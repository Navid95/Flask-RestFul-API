import logging
import os
from typing import Type

from flask import Flask

from flask_restful_core.utilities.logging.configuration import configure_logging
from flask_restful_core.utilities.logging.api_log import log_api_call, get_request_time
from flask_restful_core.utilities.exceptions import register_handlers
from flask_restful_core import blueprints
from flask_restful_core.config import Development, Test, Production
from flask_restful_core.models import BaseSchema
from flask_restful_core.models import BaseModel
from flask_restful_core.blueprints.api import BaseAPI
from flask_restful_core.blueprints.api import BaseRestAPI
from flask_restful_core.blueprints.api import BaseRestAPIById
from flask_restful_core.blueprints.api import BaseRestAPIRelationshipByModelId
from flask_restful_core.blueprints.api import BaseRestAPIRelationshipByModelIdBySubResourceId
from flask_restful_core.blueprints.service import BaseService
from flask_restful_core.extensions import db
from flask_restful_core.extensions import ma
from flask_restful_core.utilities.logging import APP_LOGGER_NAME

__version__ = '0.2.0'

ENV = os.environ.get('FLASK_ENV', 'DEVELOP')
configurations = [Development, Test, Production]
logger = logging.getLogger(APP_LOGGER_NAME)


def create_app(name, config=Development):
    app = Flask(import_name=name)
    app.config.from_object(config)
    configure_logging(app)
    logger.info('initializing the flask app ...')
    app = register_extensions(app)
    app = register_blueprints(app)
    app = register_apis(app)
    app = register_app_hooks(app)
    register_handlers(app)
    return app


def register_blueprints(app):
    return app


def register_extensions(app):
    db.init_app(app)
    ma.init_app(app)
    return app


def register_apis(app):
    return app


def register_api(app: Flask, resource: Type[BaseModel], resource_schema: Type[BaseSchema], service: Type[BaseService],
                 relations: list[tuple[[BaseModel, BaseSchema, str, [bool]]]] = None):
    _service_ = service(model=resource, schema=resource_schema, relations=relations)
    if relations:
        for relation in relations:
            api_relationship = BaseRestAPIRelationshipByModelId.as_view(
                name=generate_view_name(BaseRestAPIRelationshipByModelId, resource_schema, relation),
                sub_resource_key=relation[2],
                service=_service_
            )

            api_relationship_by_id = BaseRestAPIRelationshipByModelIdBySubResourceId.as_view(
                name=generate_view_name(BaseRestAPIRelationshipByModelIdBySubResourceId, resource_schema, relation),
                sub_resource_key=relation[2],
                service=_service_
            )

            app.add_url_rule(generate_view_uri(BaseRestAPIRelationshipByModelId, resource_schema, relation),
                             view_func=api_relationship)
            app.add_url_rule(generate_view_uri(BaseRestAPIRelationshipByModelIdBySubResourceId, resource_schema, relation),
                             view_func=api_relationship_by_id)
    rest_api = BaseRestAPI.as_view(
        name=f'{generate_view_name(BaseRestAPI, resource_schema)}',
        service=_service_
    )

    rest_api_by_id = BaseRestAPIById.as_view(
        name=f'{generate_view_name(BaseRestAPIById, resource_schema)}',
        service=_service_
    )

    app.add_url_rule(generate_view_uri(BaseRestAPI, resource_schema), view_func=rest_api)
    app.add_url_rule(generate_view_uri(BaseRestAPIById, resource_schema), view_func=rest_api_by_id)

    return app


def generate_view_name(end_point: Type[BaseAPI], resource_schema: Type[BaseSchema],
                       relation: tuple[[BaseModel, BaseSchema, str, bool]] = None) -> str:
    view_name = resource_schema.__envelope__.get("many")

    if relation:
        view_name = view_name + relation[1].__envelope__.get("many") + end_point.__view_name_suffix__
    else:
        view_name = view_name + end_point.__view_name_suffix__

    return view_name


def generate_view_uri(end_point: Type[BaseAPI], resource_schema: Type[BaseSchema],
                      relation: tuple[[BaseModel, BaseSchema, str, bool]] = None) -> str:
    view_uri = '/' + resource_schema.__envelope__.get("many")

    if end_point is BaseRestAPI:
        return view_uri
    elif end_point is BaseRestAPIById:
        return view_uri + '/' + '<uuid:id>'
    elif relation:
        if end_point is BaseRestAPIRelationshipByModelId:
            return view_uri + '/' + '<uuid:id>' + '/' + relation[1].__envelope__.get("many")
        elif end_point is BaseRestAPIRelationshipByModelIdBySubResourceId:
            return view_uri + '/' + '<uuid:model_id>' + '/' + relation[1].__envelope__.get(
                "many") + '/' + '<uuid:sub_resource_id>'
    return ''


def register_app_hooks(app):
    hook1 = app.before_request(get_request_time)
    hook2 = app.after_request(log_api_call)
    return app
