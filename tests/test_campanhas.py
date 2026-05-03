import pytest
from tests.conftest import registrar, logar, auth


CAMPANHA_BASE = {
    'titulo': 'iPhone 15 Pro Max',
    'descricao': 'Concorra a um iPhone incrível',
    'premio': 'iPhone 15 Pro Max 256GB',
    'valor_titulo': 10.00,
    'total_titulos': 1000,
    'min_quantidade_compra': 1,
    'max_quantidade_compra': 100,
}


# --- listar ---

def test_listar_campanhas_vazio(client):
    rv = client.get('/api/campanhas')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['campanhas'] == []
    assert data['total'] == 0


def test_listar_campanhas_com_filtro_status(client):
    rv = client.get('/api/campanhas?status=ativo')
    assert rv.status_code == 200


def test_listar_campanhas_com_dados(client, campanha_criada):
    rv = client.get('/api/campanhas')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total'] == 1
    c = data['campanhas'][0]
    assert c['titulo'] == 'Campanha Teste'
    assert 'progresso' in c
    assert 'totalTickets' in c


# --- detalhes ---

def test_detalhes_campanha_por_slug(client, campanha_criada):
    slug = campanha_criada['slug']
    rv = client.get(f'/api/campanhas/{slug}')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['slug'] == slug
    assert 'descricao' in data
    assert 'regulamento' in data


def test_detalhes_campanha_nao_existe(client):
    rv = client.get('/api/campanhas/slug-inexistente')
    assert rv.status_code == 404


# --- criar ---

def test_criar_campanha_sem_autenticacao(client):
    rv = client.post('/api/campanhas', json=CAMPANHA_BASE)
    assert rv.status_code == 401


def test_criar_campanha_usuario_comum(client, token_usuario):
    rv = client.post('/api/campanhas', json=CAMPANHA_BASE, headers=auth(token_usuario))
    assert rv.status_code == 403


def test_criar_campanha_admin_sucesso(client, token_admin):
    rv = client.post('/api/campanhas', json=CAMPANHA_BASE, headers=auth(token_admin))
    assert rv.status_code == 201
    data = rv.get_json()
    assert 'campanha' in data
    assert data['campanha']['titulo'] == 'iPhone 15 Pro Max'
    assert data['campanha']['slug'] is not None


def test_criar_campanha_sem_corpo(client, token_admin):
    rv = client.post('/api/campanhas', data='not json', content_type='text/plain',
                     headers=auth(token_admin))
    assert rv.status_code in (400, 415, 500)


# --- atualizar ---

def test_atualizar_campanha_admin(client, token_admin, campanha_criada):
    campanha_id = campanha_criada['public_id']
    rv = client.put(f'/api/campanhas/{campanha_id}', json={
        'titulo': 'Título Atualizado',
    }, headers=auth(token_admin))
    assert rv.status_code == 200
    assert rv.get_json()['campanha']['titulo'] == 'Título Atualizado'


def test_atualizar_campanha_sem_admin(client, token_usuario, campanha_criada):
    campanha_id = campanha_criada['public_id']
    rv = client.put(f'/api/campanhas/{campanha_id}', json={'titulo': 'X'}, headers=auth(token_usuario))
    assert rv.status_code == 403


# --- deletar ---

def test_deletar_campanha_admin(client, token_admin, campanha_criada):
    campanha_id = campanha_criada['public_id']
    rv = client.delete(f'/api/campanhas/{campanha_id}', headers=auth(token_admin))
    assert rv.status_code == 200

    rv2 = client.get(f"/api/campanhas/{campanha_criada['slug']}")
    assert rv2.status_code == 404


def test_deletar_campanha_sem_admin(client, token_usuario, campanha_criada):
    campanha_id = campanha_criada['public_id']
    rv = client.delete(f'/api/campanhas/{campanha_id}', headers=auth(token_usuario))
    assert rv.status_code == 403


# --- compradores ---

def test_buscar_compradores_sem_admin(client, token_usuario, campanha_criada):
    campanha_id = campanha_criada['public_id']
    rv = client.get(f'/api/campanhas/{campanha_id}/compradores', headers=auth(token_usuario))
    assert rv.status_code == 403


def test_buscar_compradores_admin_vazio(client, token_admin, campanha_criada):
    campanha_id = campanha_criada['public_id']
    rv = client.get(f'/api/campanhas/{campanha_id}/compradores?q=pedro', headers=auth(token_admin))
    assert rv.status_code == 200
    assert rv.get_json()['compradores'] == []


# --- títulos premiados ---

def test_adicionar_titulo_premiado(client, token_admin, campanha_criada):
    campanha_id = campanha_criada['public_id']
    rv = client.post(f'/api/campanhas/{campanha_id}/titulos-premiados', json={
        'numero_titulo': '00001',
        'valor_premio': 500.00,
    }, headers=auth(token_admin))
    assert rv.status_code == 201
    assert rv.get_json()['titulo']['numero_titulo'] == '00001'


def test_listar_titulos_premiados(client, token_admin, campanha_criada):
    slug = campanha_criada['slug']
    rv = client.get(f'/api/campanhas/{slug}/titulos-premiados')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'titulos_premiados' in data
