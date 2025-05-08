import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app('testing')  # Asegúrate de tener configuración 'testing' en tu app factory
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


def test_create_category_success(client):
    response = client.post('/api/categories/', json={"name": "Electronics"})
    data = response.get_json()
    assert response.status_code == 201
    assert data['success'] is True
    assert data['data']['name'] == "Electronics"


def test_create_category_invalid_json(client):
    response = client.post('/api/categories/', data="not-json", content_type='application/json')
    data = response.get_json()
    assert response.status_code == 400
    assert data['success'] is False


def test_get_category_success(client):
    # Primero crea una categoría
    post_resp = client.post('/api/categories/', json={"name": "Books"})
    cat_id = post_resp.get_json()['category_id']

    # Luego la consulta
    get_resp = client.get(f'/api/categories/{cat_id}')
    data = get_resp.get_json()
    assert get_resp.status_code == 200
    assert data['data']['name'] == "Books"


def test_get_category_not_found(client):
    response = client.get('/api/categories/999')
    assert response.status_code == 404


def test_list_categories(client):
    client.post('/api/categories/', json={"name": "A"})
    client.post('/api/categories/', json={"name": "B"})

    response = client.get('/api/categories/')
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 2


def test_update_category_success(client):
    post = client.post('/api/categories/', json={"name": "OldName"})
    cat_id = post.get_json()['category_id']

    response = client.put(f'/api/categories/{cat_id}', json={"name": "NewName"})
    data = response.get_json()
    assert response.status_code == 200
    assert data['data']['name'] == "NewName"


def test_update_category_not_found(client):
    response = client.put('/api/categories/999', json={"name": "Anything"})
    assert response.status_code == 404


def test_delete_category_success(client):
    post = client.post('/api/categories/', json={"name": "TempCategory"})
    cat_id = post.get_json()['category_id']

    response = client.delete(f'/api/categories/{cat_id}')
    assert response.status_code == 200
    assert response.get_json()['success'] is True


def test_delete_category_not_found(client):
    response = client.delete('/api/categories/999')
    assert response.status_code == 404
