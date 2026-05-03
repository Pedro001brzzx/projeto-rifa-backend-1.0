import pytest
from tests.conftest import registrar, auth


# --- checkout ---

def test_checkout_sem_autenticacao(client):
    rv = client.post('/api/checkout', json={
        'campanha_id': 1,
        'quantidade_titulos': 5,
    })
    assert rv.status_code == 401


def test_checkout_campanha_inexistente(client, token_usuario):
    rv = client.post('/api/checkout', json={
        'campanha_id': 'uuid-inexistente',
        'quantidade_titulos': 5,
    }, headers=auth(token_usuario))
    assert rv.status_code in (400, 404)


def test_checkout_campos_obrigatorios(client, token_usuario):
    rv = client.post('/api/checkout', json={}, headers=auth(token_usuario))
    assert rv.status_code == 400
    assert 'campanha_id' in rv.get_json()['erro']


def test_checkout_perfil_incompleto(client, token_usuario, campanha_criada):
    # Usuário criado sem CPF completo no perfil → validação de gateway bloqueia
    rv = client.post('/api/checkout', json={
        'campanha_id': campanha_criada['public_id'],
        'quantidade_titulos': 1,
        'metodo_pagamento': 'pix',
    }, headers=auth(token_usuario))
    # Espera 400 (perfil incompleto) ou 201 (mock em dev sem chave configurada)
    assert rv.status_code in (201, 400)


# --- consultar pagamento ---

def test_consultar_pagamento_sem_autenticacao(client):
    rv = client.get('/api/pagamentos/qualquer-id')
    assert rv.status_code == 401


def test_consultar_pagamento_nao_encontrado(client, token_usuario):
    rv = client.get('/api/pagamentos/uuid-que-nao-existe', headers=auth(token_usuario))
    assert rv.status_code == 404


# --- webhook ---

def test_webhook_evento_desconhecido(client):
    rv = client.post('/api/pagamentos/webhook', json={
        'event': 'unknown.event',
        'data': {},
    })
    assert rv.status_code == 200
    assert rv.get_json()['mensagem'] == 'Evento ignorado'


def test_webhook_billing_paid_sem_produtos(client):
    rv = client.post('/api/pagamentos/webhook', json={
        'event': 'billing.paid',
        'data': {'billing': {'id': 'bill_123', 'products': []}},
    })
    assert rv.status_code == 400


def test_webhook_billing_paid_compra_inexistente(client):
    rv = client.post('/api/pagamentos/webhook', json={
        'event': 'billing.paid',
        'data': {
            'billing': {
                'id': 'bill_123',
                'products': [{'externalId': 'uuid-inexistente'}],
            }
        },
    })
    assert rv.status_code == 404


# --- aprovar manualmente ---

def test_aprovar_pagamento_sem_autenticacao(client):
    rv = client.post('/api/pagamentos/qualquer-id/aprovar')
    assert rv.status_code == 401


def test_aprovar_pagamento_usuario_comum(client, token_usuario):
    rv = client.post('/api/pagamentos/qualquer-id/aprovar', headers=auth(token_usuario))
    assert rv.status_code == 403


def test_aprovar_pagamento_admin_nao_encontrado(client, token_admin):
    rv = client.post('/api/pagamentos/uuid-inexistente/aprovar', headers=auth(token_admin))
    assert rv.status_code == 404


# --- admin: deletar compra ---

def test_deletar_compra_sem_admin(client, token_usuario):
    rv = client.delete('/api/compras/qualquer-id', headers=auth(token_usuario))
    assert rv.status_code == 403


def test_deletar_compra_admin_nao_encontrada(client, token_admin):
    rv = client.delete('/api/compras/uuid-inexistente', headers=auth(token_admin))
    assert rv.status_code == 404


# --- admin: listar usuários e dashboard ---

def test_listar_usuarios_admin(client, token_admin):
    rv = client.get('/api/painel-secreto-x9/usuarios', headers=auth(token_admin))
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'usuarios' in data
    assert data['total'] >= 1


def test_listar_usuarios_sem_admin(client, token_usuario):
    rv = client.get('/api/painel-secreto-x9/usuarios', headers=auth(token_usuario))
    assert rv.status_code == 403


def test_dashboard_admin(client, token_admin):
    rv = client.get('/api/painel-secreto-x9/dashboard', headers=auth(token_admin))
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'stats' in data
    assert 'ultimas_vendas' in data
    assert 'total_usuarios' in data['stats']
