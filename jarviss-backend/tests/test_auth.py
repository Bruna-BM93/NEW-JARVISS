import pytest
from app import app, db
from models.user import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register_and_login(client):
    # Registro
    response = client.post('/register', json={
        'nome': 'Teste',
        'email': 'teste@teste.com',
        'cpf': '12345678900',
        'senha': 'senha123'
    })
    assert response.status_code == 201
    # Login
    response = client.post('/login', json={
        'email_ou_cpf': 'teste@teste.com',
        'senha': 'senha123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
