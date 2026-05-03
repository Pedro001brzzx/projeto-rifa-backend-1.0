import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture()
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


# --- helpers ---

def registrar(client, *, telefone='11999999999', email='user@test.com',
               cpf='12345678900', nome='Usuário Teste', senha='senha123'):
    return client.post('/api/auth/registro', json={
        'nome': nome,
        'telefone': telefone,
        'email': email,
        'cpf': cpf,
        'senha': senha,
    })


def logar(client, *, telefone='11999999999', senha='senha123'):
    resp = client.post('/api/auth/login', json={
        'telefone': telefone,
        'senha': senha,
    })
    return resp.get_json()['token']


def auth(token):
    return {'Authorization': f'Bearer {token}'}


# --- fixtures ---

@pytest.fixture()
def token_usuario(client):
    registrar(client)
    return logar(client)


@pytest.fixture()
def token_admin(app, client):
    registrar(client, telefone='99999999999', email='admin@test.com', cpf='00000000000')
    from app.models import Usuario
    u = Usuario.query.filter_by(telefone='99999999999').first()
    u.is_admin = True
    _db.session.commit()
    return logar(client, telefone='99999999999')


@pytest.fixture()
def campanha_criada(client, token_admin):
    resp = client.post('/api/campanhas', json={
        'titulo': 'Campanha Teste',
        'descricao': 'Descrição da campanha',
        'premio': 'iPhone 15',
        'valor_titulo': 10.00,
        'total_titulos': 100,
        'min_quantidade_compra': 1,
        'max_quantidade_compra': 50,
    }, headers=auth(token_admin))
    assert resp.status_code == 201
    return resp.get_json()['campanha']
