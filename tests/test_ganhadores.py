import pytest
from tests.conftest import auth


def test_listar_ganhadores_vazio(client):
    rv = client.get('/api/ganhadores')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['ganhadores'] == []
    assert data['total'] == 0


def test_listar_ganhadores_paginacao(client):
    rv = client.get('/api/ganhadores?page=1&per_page=10')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'paginas' in data


def test_listar_ganhadores_com_campanha_concluida(app, client, token_admin, campanha_criada):
    from app.models import Campanha, Usuario
    from app.extensions import db
    from datetime import date

    campanha = Campanha.query.filter_by(public_id=campanha_criada['public_id']).first()
    usuario = Usuario.query.filter_by(telefone='99999999999').first()

    campanha.status = 'concluido'
    campanha.ganhador_id = usuario.id
    campanha.numero_sorteado = '00001'
    campanha.data_conclusao = date.today()
    db.session.commit()

    rv = client.get('/api/ganhadores')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['total'] == 1
    g = data['ganhadores'][0]
    assert '***' in g['name']
    assert g['campaignTitle'] == 'Campanha Teste'
    assert g['luckyNumber'] == '00001'
    assert '****' in g['phone']
