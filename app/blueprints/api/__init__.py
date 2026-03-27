import logging
from uuid import UUID

from flask.views import MethodView
from flask import request
from app.blueprints.service import BaseService
from environ import APP_LOGGER_NAME

logger = logging.getLogger(APP_LOGGER_NAME)


class BaseAPI(MethodView):
    init_every_request = False
    __view_name_suffix__ = ''


class BaseRestAPIById(BaseAPI):
    """
    Generic class of all REST APIs.

    For a given model of type BaseModel produces bellow http resource end points:
    GET , DELETE -> /models/id

    Is a child class of flask's MethodView.

    Class Variables:

    - init_every_request: If false instructs flask to use 1 instance for all incoming requests which is useful if the
    state of the object should be shared across requests, By-default it is False.

    """
    init_every_request = False
    __view_name_suffix__ = 'ById'

    def __init__(self, service: BaseService):
        """
        Initiate the object.

        :param service: service layer for business logic.
        """
        self.__service__ = service

    def get(self, id: UUID):
        """
        HTTP GET, retrieve resource by given id.

        :param id: The id of the resource on DB.
        :return: Serialized presentation of the resource
        """
        return self.__service__.get_model_by_id(id)

    def delete(self, id: UUID):
        """
        HTTP DELETE, delete resource by given id.

        :param id: The id of the resource on DB.
        :return: bool
        """
        return self.__service__.delete_model_by_id(id)


class BaseRestAPI(BaseAPI):
    """
    Generic class of all REST APIs.

    For a given model of type BaseModel produces bellow http resource end points:
    POST , PUT, GET -> /models/

    Is a child class of flask's MethodView.

    Class Variables:

    - init_every_request: If false instructs flask to use 1 instance for all incoming requests which is useful if the
    state of the object should be shared across requests, By-default it is False.

        """
    init_every_request = False
    __view_name_suffix__ = ''

    def __init__(self, service: BaseService):
        """
        Initiate the object.

        :param service: service layer for business logic.
        """
        self.__service__ = service

    def post(self):
        """
        HTTP POST, create the resource by given data in request body.
        :return: Serialized presentation of the resource
        """
        return self.__service__.create_model(request.get_json())

    def put(self):
        """
        HTTP PUT, update the resource by given data in request body.
        :return: Serialized presentation of the resource
        """
        return self.__service__.update_model(request.get_json())

    def get(self):
        """
        HTTP GET, retrieve all resources, 'limit' and 'page' URL parameters are used for pagination.

        note: limit and page default values are 10 and 1 respectively.

        :return: Serialized presentation of the resources
        """
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
        except Exception as err:
            logger.error(err)
            page = 1
            limit = 10
        return self.__service__.get_all_models(limit=limit, page=page)


class BaseRestAPIRelationshipByModelId(BaseAPI):
    """
    Generic class of all REST APIs.

    For a given model of type BaseModel produces bellow http resource end points for its sub-resources:
    GET -> /models/id/sub-resources

    Is a child class of flask's MethodView.

    Class Variables:

    - init_every_request: If false instructs flask to use 1 instance for all incoming requests which is useful if the
    state of the object should be shared across requests, By-default it is False.
    """
    init_every_request = False
    __view_name_suffix__ = 'ByModelId'

    def __init__(self, sub_resource_key: str, service: BaseService):
        """
        Initiate the object.

        :param sub_resource_key: The attribute name of the sub-resource on model (i.e model.key).
        :param service: service layer for business logic.
        """
        self.__sub_resource_key__ = sub_resource_key
        self.__service__ = service

    def get(self, id: UUID):
        """
        HTTP GET, retrieve sub-resource(s).

        :param id: The id of the resource (model) on DB.
        :return: Serialized presentation of the sub-resource(s)
        """
        return self.__service__.get_sub_model(id, self.__sub_resource_key__)

    def put(self, id: UUID):
        """
        HTTP PUT, update the subresource(s) by given data in request body.

        :param id: The id of the resource (model) on DB.
        :return: Serialized presentation of the sub-resource(s)
        """

        return self.__service__.create_sub_model(id, request.get_json(), self.__sub_resource_key__)


class BaseRestAPIRelationshipByModelIdBySubResourceId(BaseAPI):
    """
    Generic class of all REST APIs.

    For a given model of type BaseModel produces bellow http resource end points for its sub-resources:
    GET, DELETE -> /models/id/sub-resources/id

    Is a child class of flask's MethodView.

    Class Variables:

    - init_every_request: If false instructs flask to use 1 instance for all incoming requests which is useful if the
    state of the object should be shared across requests, By-default it is False.
    """
    init_every_request = False
    __view_name_suffix__ = 'ByModelIdBySubResourceId'

    def __init__(self, sub_resource_key: str, service: BaseService):
        """
        Initiate the object.

        :param sub_resource_key: The attribute name of the sub-resource on model (i.e model.key).
        :param service: service layer for business logic.
        """
        self.__sub_resource_key__ = sub_resource_key
        self.__service__ = service

    def get(self, model_id: UUID, sub_resource_id: UUID):
        """
        HTTP GET, retrieve a sub-resource under a resource.

        :param model_id: The id of the resource (model) on DB.
        :param sub_resource_id: The id of the sub-resource on DB.
        :return: Serialized presentation of the sub-resource
        """
        return self.__service__.get_sub_model_by_id(model_id, sub_resource_id, self.__sub_resource_key__)

    def delete(self, model_id: UUID, sub_resource_id: UUID):
        """
        HTTP DELETE, delete a sub-resource under a resource.

        :param model_id: The id of the resource (model) on DB.
        :param sub_resource_id: The id of the sub-resource on DB.
        :return: bool
        """
        return self.__service__.delete_sub_model_by_id(model_id, sub_resource_id, self.__sub_resource_key__)
