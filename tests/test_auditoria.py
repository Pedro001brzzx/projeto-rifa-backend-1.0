"""
Testes para auditoria do sorteio (Ponto 7 — Fase A)

Verifica que:
- O endpoint GET /api/{admin_prefix}/campanhas/{id}/auditoria exige autenticação admin
- Retorna 404 para campanha inexistente
- Retorna o histórico de AdminLog após a definição de um ganhador
- Suporta paginação (?page, ?per_page)
"""

import os
import pytest
from tests.conftest import auth


ADMIN_PREFIX = os.environ.get('ADMIN_ROUTE_SECRET', '/api/painel-secreto-x9')


def _url_auditoria(campanha_id):
    return f'{ADMIN_PREFIX}/campanhas/{campanha_id}/auditoria'


# --------------------------------------------------------------------------
# Acesso e autenticação
# --------------------------------------------------------------------------

def test_auditoria_sem_autenticacao(client, campanha_criada):
    rv = client.get(_url_auditoria(campanha_criada['public_id']))
    assert rv.status_code == 401


def test_auditoria_usuario_comum(client, campanha_criada, token_usuario):
    rv = client.get(
        _url_auditoria(campanha_criada['public_id']),
        headers=auth(token_usuario),
    )
    assert rv.status_code == 403


def test_auditoria_campanha_inexistente(client, token_admin):
    rv = client.get(
        _url_auditoria('uuid-inexistente-0000'),
        headers=auth(token_admin),
    )
    assert rv.status_code == 404


# --------------------------------------------------------------------------
# Estrutura da resposta
# --------------------------------------------------------------------------

def test_auditoria_estrutura_resposta_vazia(client, campanha_criada, token_admin):
    """Campanha sem nenhum log ainda deve retornar estrutura correta."""
    rv = client.get(
        _url_auditoria(campanha_criada['public_id']),
        headers=auth(token_admin),
    )
    assert rv.status_code == 200
    data = rv.get_json()

    assert 'campanha_id' in data
    assert 'campanha_titulo' in data
    assert 'auditoria' in data
    assert isinstance(data['auditoria'], list)
    assert 'total' in data
    assert 'pagina' in data
    assert 'por_pagina' in data
    assert 'paginas' in data


# --------------------------------------------------------------------------
# Registro pós-sorteio
# --------------------------------------------------------------------------

def test_auditoria_registra_definicao_ganhador(app, client, campanha_criada, token_usuario, token_admin):
    """
    Após definir o ganhador via endpoint, o AdminLog deve conter ao menos
    1 entrada e a auditoria da campanha deve refletir isso.

    A compra é injetada diretamente no banco (sem AbacatePay) seguindo
    o padrão de test_ganhadores.py.
    """
    from app.models import Campanha, Usuario, Compra
    from app.models.titulo import Titulo
    from app.extensions import db
    import uuid

    campanha_public_id = campanha_criada['public_id']

    with app.app_context():
        campanha = Campanha.query.filter_by(public_id=campanha_public_id).first()
        usuario = Usuario.query.filter_by(email='user@test.com').first()

        # Criar compra aprovada diretamente no banco
        compra = Compra(
            public_id=str(uuid.uuid4()),
            campanha_id=campanha.id,
            usuario_id=usuario.id,
            quantidade_titulos=1,
            valor_total=campanha.valor_titulo or 10.0,
            status_pagamento='aprovado',
        )
        db.session.add(compra)
        db.session.flush()

        # Criar título associado
        titulo = Titulo(
            campanha_id=campanha.id,
            compra_id=compra.id,
            numero='000001',
        )
        db.session.add(titulo)
        db.session.commit()

        compra_id = compra.id
        titulo_id = titulo.id

    # Definir ganhador via endpoint
    rv_ganhador = client.post(
        f'/api/campanhas/{campanha_public_id}/ganhador',
        json={'compra_id': compra_id, 'titulo_id': titulo_id, 'metodo': 'manual'},
        headers=auth(token_admin),
    )
    assert rv_ganhador.status_code == 200, rv_ganhador.get_json()

    # Consultar auditoria
    rv_audit = client.get(
        _url_auditoria(campanha_public_id),
        headers=auth(token_admin),
    )
    assert rv_audit.status_code == 200
    data = rv_audit.get_json()

    assert data['total'] >= 1
    assert len(data['auditoria']) >= 1

    # Verificar campos do log
    entrada = data['auditoria'][0]
    assert 'action' in entrada
    assert 'details' in entrada
    assert 'created_at' in entrada
    assert 'admin_name' in entrada


# --------------------------------------------------------------------------
# Paginação
# --------------------------------------------------------------------------

def test_auditoria_paginacao(client, campanha_criada, token_admin):
    """Parâmetros page e per_page são refletidos na resposta."""
    rv = client.get(
        _url_auditoria(campanha_criada['public_id']) + '?page=1&per_page=5',
        headers=auth(token_admin),
    )
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['pagina'] == 1
    assert data['por_pagina'] == 5
