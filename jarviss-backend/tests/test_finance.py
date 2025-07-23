import pytest
from app import app, db
from models.user import User
from flask_jwt_extended import create_access_token

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

def criar_usuario_e_token():
    user = User(nome='Financeiro', email='fin@fin.com', cpf='11122233344', senha_hash='hash')
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id)
    return user, token

def test_nova_transacao_listar_resumo(client):
    with app.app_context():
        user, token = criar_usuario_e_token()
    headers = {'Authorization': f'Bearer {token}'}
    # Cadastrar receita
    resp = client.post('/transacoes', json={
        'tipo': 'receita', 'valor': 100.0, 'descricao': 'Venda', 'data': '2024-01-01'
    }, headers=headers)
    assert resp.status_code == 201
    # Cadastrar despesa
    resp = client.post('/transacoes', json={
        'tipo': 'despesa', 'valor': 40.0, 'descricao': 'Compra', 'data': '2024-01-02'
    }, headers=headers)
    assert resp.status_code == 201
    # Listar
    resp = client.get('/transacoes', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    # Resumo
    resp = client.get('/resumo', headers=headers)
    resumo = resp.get_json()
    assert resumo['saldo'] == 60.0
    assert resumo['entradas'] == 100.0
    assert resumo['saidas'] == 40.0
