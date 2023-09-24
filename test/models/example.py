from uuid import UUID
from typing import List

import marshmallow.fields
from sqlalchemy import Table

from app.models import BaseModel, BaseSchema
from app.extensions import db
from app.extensions import ma

child_class = Table(
    "child_class",
    BaseModel.metadata,
    db.Column("school_class_id", db.ForeignKey("school_class.id")),
    db.Column("child_id", db.ForeignKey("child.id")),
)


class SingleParent(BaseModel):
    name: db.Mapped[str] = db.mapped_column(nullable=False)

    children: db.Mapped[List['Child']] = db.relationship(
        primaryjoin="and_(SingleParent.id == Child.parent_id, Child.active)")


class Child(BaseModel):
    name: db.Mapped[str] = db.mapped_column(nullable=False)
    parent_id: db.Mapped[UUID] = db.mapped_column(db.ForeignKey('single_parent.id'), nullable=True)

    parent: db.Mapped['SingleParent'] = db.relationship(
        primaryjoin="and_(SingleParent.id == Child.parent_id, SingleParent.active)")
    classes: db.Mapped[List['SchoolClass']] = db.relationship(
        secondary=child_class,
        primaryjoin='and_(Child.id == child_class.c.child_id, Child.active)',
        secondaryjoin='and_(SchoolClass.id == child_class.c.school_class_id, SchoolClass.active)',
        back_populates='attendees'
    )


class SchoolClass(BaseModel):
    name: db.Mapped[str] = db.mapped_column()
    attendees: db.Mapped[List['Child']] = db.relationship(
        secondary=child_class,
        primaryjoin='and_(SchoolClass.id == child_class.c.school_class_id, SchoolClass.active)',
        secondaryjoin='and_(Child.id == child_class.c.child_id, Child.active)',
        back_populates='classes'
    )


# marshmallow schemas


class ParentSchema(BaseSchema):
    __envelope__ = {'single': 'parent', 'many': 'parents'}

    class Meta:
        model = SingleParent

    children = ma.auto_field()


class ChildSchema(BaseSchema):
    __envelope__ = {'single': 'child', 'many': 'children'}

    class Meta:
        model = Child

    parent = ma.auto_field()
    classes = ma.auto_field()


class SchoolClassSchema(BaseSchema):
    __envelope__ = {'single': 'schoolClass', 'many': 'schoolClasses'}

    class Meta:
        model = SchoolClass

    attendees = ma.auto_field()
