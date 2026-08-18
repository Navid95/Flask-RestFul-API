# Flask REST API Framework

![Tests](https://github.com/Navid95/flask-restfull-tutorial/actions/workflows/tests.yml/badge.svg)

A framework for building Flask REST APIs without writing repetitive boilerplate. Define your model, define your schema, register them — and get a fully working API with serialization, pagination, and relationship endpoints handled automatically. Your only job is the business logic.

Built while working on a Flask project professionally, after seeing colleagues rely on extensions like flask-smorest to cut down boilerplate. I wanted to understand how much of that "register and forget" feel I could recreate myself, and end up with something reusable in future projects.

## The Problem It Solves

Every CRUD API requires the same scaffolding: route handlers, serialization, deserialization, pagination, relationship endpoints. This framework generates all of that from a single call:

```python
register_api(app, Order, OrderSchema, BaseService, [(Item, ItemSchema, 'items', True)])
```

That one line produces 9 endpoints, handles JSON serialization/deserialization via Marshmallow, and wires up the `Order → Items` relationship — including nested endpoints.

## What You Get For Free

Every registered model automatically has:

| Feature | Detail |
|---|---|
| UUID primary key | Auto-generated, no sequential IDs |
| Timestamps | `created` and `updated`, managed automatically |
| Soft delete | `DELETE` sets `active=False`, data is never lost |
| Pagination | `?page=1&limit=10` on every collection endpoint |
| Envelope wrapping | Consistent `{ "order": {...} }` / `{ "orders": [...] }` responses |
| Relationship endpoints | Full sub-resource CRUD for declared relationships |
| Request logging | Every request/response logged as structured JSON, to stdout by default |

## Auto-Generated Endpoints

```python
register_api(app, Parent, ParentSchema, BaseService, [(Child, ChildSchema, 'children', True)])
```

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/parents` | List all, paginated |
| `POST` | `/parents` | Create |
| `PUT` | `/parents` | Update |
| `GET` | `/parents/<id>` | Get by ID |
| `DELETE` | `/parents/<id>` | Soft delete |
| `GET` | `/parents/<id>/children` | List children |
| `PUT` | `/parents/<id>/children` | Set children |
| `GET` | `/parents/<id>/children/<child_id>` | Get specific child |
| `DELETE` | `/parents/<id>/children/<child_id>` | Remove child |

## Customizing Business Logic

`BaseService` handles all the generic CRUD behaviour. To add custom logic, subclass it and override only the methods you need — everything else keeps working as before:

```python
class OrderService(BaseService):

    def create_model(self, request_data: dict = None):
        # custom logic before/after creation: validate stock, send notification, etc.
        ...
        return super().create_model(request_data)

    def delete_model_by_id(self, model_id):
        # e.g. cancel related payments before deleting
        ...
        return super().delete_model_by_id(model_id)

register_api(app, Order, OrderSchema, OrderService)
```

All other endpoints (`get`, `update`, `get_all`, relationship endpoints) continue to use the base implementation untouched.

## Defining a Model

```python
from flask_restful_core.models import BaseModel, BaseSchema
from flask_restful_core.extensions import db

class Parent(BaseModel):
    name: db.Mapped[str] = db.mapped_column(nullable=False)
    children: db.Mapped[List['Child']] = db.relationship(
        primaryjoin="and_(Parent.id == Child.parent_id, Child.active)")

class ParentSchema(BaseSchema):
    __envelope__ = {'single': 'parent', 'many': 'parents'}

    class Meta:
        model = Parent
        include_fk = True
```

`BaseSchema` uses Marshmallow's `SQLAlchemyAutoSchema` — fields are introspected from the model automatically. No manual field declarations needed.

## Stack

- Python 3.10
- Flask 2.3
- SQLAlchemy 2.0
- Marshmallow 3.20

## Installing as a Dependency

The package (`flask_restful_core`) is pip-installable directly from this repo, so another project can depend
on it as a library instead of copying the code:

```bash
pip install git+https://github.com/Navid95/Flask-RestFul-API.git
```

Then, from anywhere in the consuming project:

```python
from flask_restful_core import create_app, register_api
from flask_restful_core.models import BaseModel, BaseSchema
from flask_restful_core.blueprints.service import BaseService
```

No special config file is required — `create_app()` reads its settings from environment variables (see
below) or a custom config class passed in as the second argument.

## Logging

Every request/response is logged as a single JSON line via two loggers, `app_logger` and `api_logger`.
Destination is controlled with environment variables (see `.env.example`):

| Variable | Default | Values |
|---|---|---|
| `LOG_DESTINATION` | `stdout` | `stdout`, `file`, `both` |
| `LOG_DIR` | `./log` | directory for file handlers (only used when `LOG_DESTINATION` includes `file`) |
| `LOG_LEVEL` | `DEBUG` | any standard `logging` level name |

`stdout` (the default) is the Docker/container-friendly mode — JSON lines on stdout are picked up by any log
driver or shipping agent (Fluentd, Promtail, Datadog agent, CloudWatch, …) with no volume mounts required.

## Quick Start

### Local

```bash
git clone https://github.com/Navid95/flask-restfull-tutorial.git
cd flask-restfull-tutorial/source
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

### Docker

```bash
cp .env.example .env
docker compose up
```

The API will be available at `http://localhost:5000`.

## Running Tests

```bash
python -m pytest test/ -v
```

## Project Structure

```
source/
├── pyproject.toml           # Packaging — pip install git+... installs flask_restful_core
├── flask_restful_core/
│   ├── __init__.py          # App factory, register_api()
│   ├── config.py            # Development/Test/Production config, env-var-driven
│   ├── blueprints/
│   │   ├── api/              # MethodView classes — HTTP layer, never touch these
│   │   └── service/          # BaseService — override here for custom business logic
│   ├── models/
│   │   └── __init__.py       # BaseModel (CRUD), BaseSchema (serialization)
│   └── utilities/
│       ├── exceptions/       # Error handlers
│       └── logging/          # Structured JSON logging, configurable destination
└── test/
    ├── models/example.py    # Example: SingleParent → Child (one-to-many), Child ↔ SchoolClass (many-to-many)
    ├── test_base_model.py
    ├── test_base_rest_api.py
    └── test_marshmallow_schema.py
```
