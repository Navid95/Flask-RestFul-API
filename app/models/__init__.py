import copy
import logging
from datetime import datetime
from uuid import UUID
from uuid import uuid4
from typing import Optional

from marshmallow import post_load
from marshmallow import pre_load
from marshmallow import post_dump
from marshmallow import ValidationError
from sqlalchemy import select
from sqlalchemy import inspect

from app.extensions import db
from app.extensions import ma
from environ import APP_LOGGER_NAME

logger = logging.getLogger(APP_LOGGER_NAME)


class BaseModel(db.Model):
    """
    Base class of all DB models.

    All models should inherit from this class to get the CRUD operations as class_methods and can use BaseSchema(marshmallow)
    for serialization/deserialization operations.

    Model attributes:

     - id (UUID): Primary key of the table, used for all operations on DB that needs to be done on a specific instance, auto generated.
     - created (datetime): Time of instance creation, auto generated.
     - updated (datetime): Time of the latest update of the instance, auto generated.
     - active (bool): Flag to determine if instance is available or deleted, defaults to True (available).

    Class Variables:

    - __abstract__: Instructs sqlalchemy not to create a table for this class. __abstract__ is not inherited by child
    classes, meaning if there is a need to create a class without a DB table associated with it this class variable
    should be set to 'True' explicitly.

    - __put_ignore_set__: Attributes in this set will be skipped during updates with put method. By-default it contains
    'id', 'created', 'updated' and 'active'.

    - __patch_ignore_set__: Attributes in this set will be skipped during updates with patch method. Initially this list
    is a deep copy of __put_ignore_set__. By-default it contains 'id', 'created', 'updated' and 'active'.

    """
    __abstract__ = True
    __put_ignore_set__ = {'id', 'created', 'updated', 'active'}
    __patch_ignore_set__ = copy.deepcopy(__put_ignore_set__)

    id: db.Mapped[UUID] = db.mapped_column(
        primary_key=True,
        default=uuid4
    )
    created: db.Mapped[datetime] = db.mapped_column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )
    updated: db.Mapped[datetime] = db.mapped_column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )
    active: db.Mapped[bool] = db.mapped_column(
        default=True,
        index=True
    )

    def to_json(self) -> dict:
        """
        Return a dict containing db columns of the model.

        Uses sqlalchemy inspect to find the columns.

        :return: Json representation of the object as a python dict
        """
        object_dict = dict()
        for column in inspect(self).mapper.column_attrs:
            value = getattr(self, column.key)
            if isinstance(value, datetime):
                object_dict[column.key] = value.isoformat()
            elif isinstance(value, BaseModel):
                object_dict[column.key] = value.to_json()
            else:
                object_dict[column.key] = value

        return object_dict

    @classmethod
    def post(cls, model_object) -> Optional[object]:
        """
        Create a new model object in the DB.

        If any exception happens, calls rollback() method of sqlalchemy.

        :param model_object: A python object of the class 'cls'.
        :return: Created object on DB | None
        """
        if not isinstance(model_object, cls):
            return None
        if model_object.id:
            return None
        try:
            db.session.add(model_object)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return None
        return model_object

    @classmethod
    def get(cls, id: UUID) -> Optional[object]:
        """
        Retrieve the object associated with the given id from DB.

        :param id: The id of the object on DB.
        :return: Retrieved object from DB | None
        """
        model_object = db.session.scalar(select(cls).where(cls.id == id).where(cls.active == True))
        return model_object

    @classmethod
    def patch(cls, id: UUID, **kwargs) -> Optional[object]:
        """
        Update the object having the id given on DB.

        Only given columns (attributes) in kwargs will be updated, rest of the columns will remain intact.
        If any exception happens, calls rollback() method of sqlalchemy.

        :param id: The id of the object on DB.
        :param kwargs: Columns of the object and their respective value.
        :return: Updated object on DB | None
        """
        model_object = cls.get(id)
        if not model_object:
            return None
        for key, value in kwargs.items():
            if key not in cls.__patch_ignore_set__:
                try:
                    setattr(model_object, key, value)
                except Exception as e:
                    logger.error(e)
                    return None
        try:
            db.session.add(model_object)
            db.session.commit()
            return model_object
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return None

    @classmethod
    def put(cls, model_object) -> Optional[object]:
        """
        Update the object having the same id as the given object on DB.

        All columns (attributes) of the object will be updated. Loops over the given object's columns using the
        sqlalchemy inspect func to find the columns and update the DB instance (retrieved by id).
        If any exception happens, calls rollback() method of sqlalchemy.

        :param model_object: A python object of the class 'cls'.
        :return: Updated object on DB | None
        """
        server_object = cls.get(model_object.id)
        if not server_object:
            return None
        try:
            for column in inspect(model_object).mapper.column_attrs:
                value = getattr(model_object, column.key)
                if column.key not in cls.__put_ignore_set__:
                    setattr(server_object, column.key, value)
            db.session.add(server_object)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return None
        return server_object

    @classmethod
    def delete(cls, id: UUID) -> bool:
        """
        Soft delete the object on DB by given id.

        Sets the active flag of the object to False and persists it on DB.
        If any exception happens, calls rollback() method of sqlalchemy.

        :param id: The id of the object on DB.
        :return: True on success | False
        """
        model_object = cls.get(id)
        if not model_object:
            return False
        model_object.active = False
        try:
            db.session.add(model_object)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return False

    @classmethod
    def get_all(cls, limit: int = 10, page: int = 1) -> list[object | None]:
        """
        Retrieve the list of all objects of class 'cls' from DB.

        Only active == True objects will be retrieved.
        Limit and page parameters will be passed to sqlalchemy's paginate func (per_page, page respectively).

        :param limit: Number of objects to return.
        :param page: Number of the page.
        :return: List of objects | empty list
        """
        model_object_list = db.paginate(
            select(cls).where(cls.active == True),
            per_page=limit,
            page=page
        )
        return model_object_list.items


class BaseSchema(ma.SQLAlchemyAutoSchema):
    """
    Base class of all Marshmallow schemas.

    All schemas should inherit from this class to get the pre_load, post_load, pre_dump and post_dump operations.
    Child classes should contain 'class Meta' with 'model = cls(BaseModel)'.

    Class Variables:

    - __envelope__: This dict contains singular and collection labels for the model that will be used in
    wrapping/unwrapping the data, By-default labels are 'model' for single and 'models' for many.

    note: Child classes should overwrite this dict values (keys should not be changed! ).
    """

    __envelope__ = {'single': 'model', 'many': 'models'}

    @post_load(pass_many=True)
    def make_model(self, data, **kwargs):
        """
        Return object instead of dict after deserialization.

        If 'many' is available and set to True in kwargs, a list of models will be returned.

        :param data: Data passed to schema.load().
        :param kwargs: Kwargs passed to schema.load().
        :return: self.Meta.model(**data) | list[models]
        """
        many = kwargs.get('many', False)

        if not many:
            return self.Meta.model(**data)
        else:
            models = list()
            for item in data:
                models.append(self.Meta.model(**item))
            return models

    @post_dump(pass_many=True)
    def handle_single_or_collection(self, data, **kwargs):
        """
        Wrapp the serialized presentation with appropriate labeling based on the 'many' keyword's value.
        Attribute self.__envelope__ is used to get labels.
        If 'many' is not available in kwargs, it is considered as False and single label is used.

        :param data: Data passed to schema.dump().
        :param kwargs: Kwargs passed to schema.dump().
        :return: { label : data }
        """
        if kwargs.get('many', False):
            return {self.__envelope__.get('many', 'models'): data}
        return {self.__envelope__.get('single', 'model'): data}

    @pre_load(pass_many=True)
    def load_with_wrapper(self, data, **kwargs):
        """
        Unwrap the data before deserialization based on the 'many' keyword's value.
        Attribute self.__envelope__ is used to get labels.
        If 'many' is not available in kwargs, it is considered as False and single label is used.

        :param data: Data passed to schema.load().
        :param kwargs: Kwargs passed to schema.load().
        :return: Raw data for deserialization

        :raises ValidationError If label is missing from input data.
        """
        if kwargs.get('many', False):
            key = self.__envelope__.get('many', 'models')
        else:
            key = self.__envelope__.get('single', 'model')
        if key not in data.keys():
            raise ValidationError(f'key: {key}, is missing in input data')
        else:
            return data[key]
