import pytest
from tests.conftest import registrar, logar, auth


DADOS_VALIDOS = dict(
    telefone='11999999999',
    email='user@test.com',
    cpf='12345678900',
    nome='Usuário Teste',
    senha='senha123',
)


# --- registro ---

def test_registro_sucesso(client):
    rv = registrar(client)
    assert rv.status_code == 201
    data = rv.get_json()
    assert 'token' in data
    assert data['usuario']['nome'] == 'Usuário Teste'
    assert 'cpf' in data['usuario']  # mascarado, mas presente


def test_registro_campo_obrigatorio_faltando(client):
    rv = client.post('/api/auth/registro', json={'nome': 'Só Nome'})
    assert rv.status_code == 400


def test_registro_cpf_invalido(client):
    rv = client.post('/api/auth/registro', json={**DADOS_VALIDOS, 'cpf': '123'})
    assert rv.status_code == 400


def test_registro_telefone_duplicado(client):
    registrar(client)
    rv = registrar(client, email='outro@test.com', cpf='98765432100')
    assert rv.status_code == 400
    assert 'Telefone' in rv.get_json()['erro']


def test_registro_email_duplicado(client):
    registrar(client)
    rv = registrar(client, telefone='11888888888', cpf='98765432100')
    assert rv.status_code == 400
    assert 'Email' in rv.get_json()['erro']


def test_registro_cpf_duplicado(client):
    registrar(client)
    rv = registrar(client, telefone='11888888888', email='outro@test.com')
    assert rv.status_code == 400
    assert 'CPF' in rv.get_json()['erro']


# --- login ---

def test_login_sucesso(client):
    registrar(client)
    rv = client.post('/api/auth/login', json={
        'telefone': '11999999999',
        'senha': 'senha123',
    })
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'token' in data
    assert data['mensagem'] == 'Login realizado com sucesso'


def test_login_senha_invalida(client):
    registrar(client)
    rv = client.post('/api/auth/login', json={
        'telefone': '11999999999',
        'senha': 'errada',
    })
    assert rv.status_code == 401


def test_login_usuario_inexistente(client):
    rv = client.post('/api/auth/login', json={
        'telefone': '00000000000',
        'senha': 'qualquer',
    })
    assert rv.status_code == 401


def test_login_campos_faltando(client):
    rv = client.post('/api/auth/login', json={'telefone': '11999999999'})
    assert rv.status_code == 400


# --- perfil ---

def test_perfil_sem_token(client):
    rv = client.get('/api/auth/perfil')
    assert rv.status_code == 401


def test_perfil_com_token(client, token_usuario):
    rv = client.get('/api/auth/perfil', headers=auth(token_usuario))
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'nome' in data
    assert 'telefone' in data


def test_atualizar_perfil(client, token_usuario):
    rv = client.put('/api/auth/perfil', json={
        'nome': 'Nome Atualizado',
        'cidade': 'Recife',
        'estado': 'PE',
    }, headers=auth(token_usuario))
    assert rv.status_code == 200
    assert rv.get_json()['usuario']['nome'] == 'Nome Atualizado'


def test_atualizar_perfil_sem_token(client):
    rv = client.put('/api/auth/perfil', json={'nome': 'X'})
    assert rv.status_code == 401


# --- logout ---

def test_logout(client, token_usuario):
    rv = client.post('/api/auth/logout', headers=auth(token_usuario))
    assert rv.status_code == 200


# --- recuperação de senha ---

def test_forgot_password_sempre_200(client):
    rv = client.post('/api/auth/forgot-password', json={'email': 'naoexiste@test.com'})
    assert rv.status_code == 200
    assert 'mensagem' in rv.get_json()


def test_forgot_password_sem_email(client):
    rv = client.post('/api/auth/forgot-password', json={})
    assert rv.status_code == 400


def test_reset_password_token_invalido(client):
    rv = client.post('/api/auth/reset-password', json={
        'token': 'token-invalido',
        'senha': 'novaSenha123',
    })
    assert rv.status_code == 400


def test_reset_password_senha_curta(client):
    rv = client.post('/api/auth/reset-password', json={
        'token': 'qualquer',
        'senha': '123',
    })
    assert rv.status_code == 400
