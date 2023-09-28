from test import app
from test import client
from test.models.example import SingleParent
from test.models.example import SingleParentSchema
from test.models.example import Child


def test_get_api(client):
    parent1 = SingleParent(name='parent1')
    SingleParent.post(parent1)
    response = client.get(f'/parents/{parent1.id.__str__()}')
    assert response.status_code == 200
    response = client.get(f'/parents/1')
    assert response.status_code == 404


def test_post_api(client):
    parent1 = SingleParent(name='parent1')
    parent_schema = SingleParentSchema(only=('name', 'children'))
    response = client.post(f'/parents/', json=parent_schema.dump(parent1))
    assert response.status_code == 200
    assert 'parent' in response.json.keys()


def test_put_api(client):
    parent1 = SingleParent(name='parent1')
    parent_schema = SingleParentSchema(only=('name', 'children'))
    response = client.post(f'/parents/', json=parent_schema.dump(parent1))

    assert response.status_code == 200
    assert 'parent' in response.json.keys()
    assert response.json['parent']

    parent1 = SingleParentSchema().load({'parent': response.json['parent']})
    parent_schema2 = SingleParentSchema(exclude=('created', 'updated', 'children'))
    json_data = parent_schema2.dump(parent1)
    json_data['parent']['name'] = 'updated name for parent 1'
    response2 = client.put(f'/parents/', json=json_data)

    assert response2.status_code == 200
    assert 'parent' in response2.json.keys()
    assert response2.json['parent']
    assert response2.json['parent']['name'] == json_data['parent']['name']