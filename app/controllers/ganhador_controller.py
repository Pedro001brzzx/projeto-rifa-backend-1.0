"""
Controller de Ganhadores
Contém a lógica de negócio para listagem de ganhadores
"""

from app.models import Campanha


def listar_ganhadores(page=1, per_page=20):
    """
    Lista os ganhadores de campanhas concluídas
    
    Args:
        page: Número da página
        per_page: Itens por página
    
    Returns:
        tuple: (response dict, status code)
    """
    campanhas = Campanha.query.filter(
        Campanha.status == 'concluido',
        Campanha.ganhador_id.isnot(None)
    ).order_by(Campanha.data_sorteio.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return {
        'ganhadores': [c.to_dict() for c in campanhas.items],
        'total': campanhas.total,
        'paginas': campanhas.pages
    }, 200
