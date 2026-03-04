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
    ).order_by(Campanha.data_conclusao.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    ganhadores = []
    for c in campanhas.items:
        ganhador_data = {
            'id': c.public_id,
            'name': c.ganhador.nome.split()[0] + ' ***' if c.ganhador else '',
            'campaignTitle': c.titulo,
            'prize': c.premio or '',
            'luckyNumber': c.numero_sorteado or '',
            'drawDate': c.data_conclusao.strftime('%d/%m/%Y') if c.data_conclusao else '',
            'phone': '',
        }
        
        # Mask phone
        if c.ganhador and c.ganhador.telefone:
            phone = c.ganhador.telefone
            if len(phone) >= 4:
                ganhador_data['phone'] = f'(**) *****-{phone[-4:]}'
            else:
                ganhador_data['phone'] = '(**) *****-****'
        
        ganhadores.append(ganhador_data)
    
    return {
        'ganhadores': ganhadores,
        'total': campanhas.total,
        'paginas': campanhas.pages
    }, 200
