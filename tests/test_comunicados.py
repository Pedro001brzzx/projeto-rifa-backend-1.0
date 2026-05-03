import pytest
from tests.conftest import auth


# --- comunicados ---

def test_listar_comunicados_vazio(client):
    rv = client.get('/api/comunicados')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['comunicados'] == []
    assert data['total'] == 0
    assert data['pagina'] == 1
    assert data['por_pagina'] == 10
    assert data['paginas'] == 0


def test_criar_comunicado_sem_autenticacao(client):
    rv = client.post('/api/comunicados', json={
        'titulo': 'Aviso',
        'conteudo': 'Texto do aviso',
    })
    assert rv.status_code == 401


def test_criar_comunicado_usuario_comum(client, token_usuario):
    rv = client.post('/api/comunicados', json={
        'titulo': 'Aviso',
        'conteudo': 'Texto',
    }, headers=auth(token_usuario))
    assert rv.status_code == 403


def test_criar_comunicado_admin(client, token_admin):
    rv = client.post('/api/comunicados', json={
        'titulo': 'Manutenção',
        'conteudo': 'Sistema em manutenção das 22h às 23h.',
        'tipo': 'aviso',
    }, headers=auth(token_admin))
    assert rv.status_code == 201
    data = rv.get_json()
    assert data['comunicado']['titulo'] == 'Manutenção'
    assert data['comunicado']['tipo'] == 'aviso'


def test_listar_comunicados_apos_criacao(client, token_admin):
    client.post('/api/comunicados', json={
        'titulo': 'Aviso 1', 'conteudo': 'Conteúdo 1',
    }, headers=auth(token_admin))

    rv = client.get('/api/comunicados')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total'] == 1
    assert len(data['comunicados']) == 1
    assert 'pagina' in data
    assert 'paginas' in data
    assert 'por_pagina' in data


def test_paginacao_page_e_per_page(client, token_admin):
    """Verifica que ?page e ?per_page funcionam corretamente."""
    # Cria 5 comunicados
    for i in range(1, 6):
        client.post('/api/comunicados', json={
            'titulo': f'Comunicado {i}',
            'conteudo': f'Conteúdo do comunicado {i}',
        }, headers=auth(token_admin))

    # Página 1, 2 por página → 2 itens
    rv = client.get('/api/comunicados?page=1&per_page=2')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total'] == 5
    assert len(data['comunicados']) == 2
    assert data['pagina'] == 1
    assert data['por_pagina'] == 2
    assert data['paginas'] == 3

    # Página 3, 2 por página → 1 item
    rv2 = client.get('/api/comunicados?page=3&per_page=2')
    data2 = rv2.get_json()
    assert len(data2['comunicados']) == 1
    assert data2['pagina'] == 3


def test_paginacao_per_page_maximo_50(client, token_admin):
    """per_page não pode ultrapassar 50."""
    # Cria 3 comunicados
    for i in range(1, 4):
        client.post('/api/comunicados', json={
            'titulo': f'Aviso {i}',
            'conteudo': f'Texto {i}',
        }, headers=auth(token_admin))

    # Solicita 200 por página → deve ser limitado a 50
    rv = client.get('/api/comunicados?per_page=200')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['por_pagina'] <= 50


def test_paginacao_pagina_inexistente(client, token_admin):
    """Página além do total retorna lista vazia sem erro."""
    client.post('/api/comunicados', json={
        'titulo': 'Único', 'conteudo': 'Texto',
    }, headers=auth(token_admin))

    rv = client.get('/api/comunicados?page=999')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['comunicados'] == []
    assert data['total'] == 1


def test_criar_comunicado_campos_obrigatorios(client, token_admin):
    rv = client.post('/api/comunicados', json={'titulo': 'Só Título'}, headers=auth(token_admin))
    assert rv.status_code == 400


def test_atualizar_comunicado_admin(client, token_admin):
    resp = client.post('/api/comunicados', json={
        'titulo': 'Original', 'conteudo': 'Texto original',
    }, headers=auth(token_admin))
    comunicado_id = resp.get_json()['comunicado']['id']

    rv = client.put(f'/api/comunicados/{comunicado_id}', json={
        'titulo': 'Atualizado',
        'ativo': False,
    }, headers=auth(token_admin))
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['comunicado']['titulo'] == 'Atualizado'
    assert data['comunicado']['ativo'] is False


def test_atualizar_comunicado_nao_existe(client, token_admin):
    rv = client.put('/api/comunicados/9999', json={'titulo': 'X'}, headers=auth(token_admin))
    assert rv.status_code == 404


def test_deletar_comunicado_admin(client, token_admin):
    resp = client.post('/api/comunicados', json={
        'titulo': 'Para Deletar', 'conteudo': 'Texto',
    }, headers=auth(token_admin))
    comunicado_id = resp.get_json()['comunicado']['id']

    rv = client.delete(f'/api/comunicados/{comunicado_id}', headers=auth(token_admin))
    assert rv.status_code == 200

    rv2 = client.get('/api/comunicados')
    assert rv2.get_json()['total'] == 0


def test_deletar_comunicado_sem_admin(client, token_usuario):
    rv = client.delete('/api/comunicados/1', headers=auth(token_usuario))
    assert rv.status_code == 403


# --- contato ---

def test_enviar_contato_sucesso(client):
    rv = client.post('/api/contato', json={
        'nome': 'João Silva',
        'email': 'joao@email.com',
        'mensagem': 'Tenho uma dúvida sobre o sorteio.',
    })
    assert rv.status_code == 201
    assert 'mensagem' in rv.get_json()


def test_enviar_contato_campos_faltando(client):
    rv = client.post('/api/contato', json={
        'nome': 'João Silva',
        'email': 'joao@email.com',
    })
    assert rv.status_code == 400


def test_enviar_contato_com_telefone_opcional(client):
    rv = client.post('/api/contato', json={
        'nome': 'Maria',
        'email': 'maria@email.com',
        'mensagem': 'Olá!',
        'telefone': '11999999999',
        'assunto': 'Dúvida',
    })
    assert rv.status_code == 201


# --- artigos ---

def test_listar_artigos_vazio(client):
    rv = client.get('/api/artigos')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'artigos' in data
    assert data['artigos'] == []


def test_artigo_nao_encontrado(client):
    rv = client.get('/api/artigos/slug-inexistente')
    assert rv.status_code == 404
