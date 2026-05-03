"""
Controller Administrativo
Contém lógica para funcionalidades exclusivas de administradores
"""

from app.models import db, Usuario, Compra, Campanha
from app.models.admin_log import AdminLog
from sqlalchemy import func
import json

def listar_usuarios(page=1, per_page=20):
    """Lista todos os usuários cadastrados"""
    users = Usuario.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'usuarios': [u.to_dict() for u in users.items],
        'total': users.total,
        'paginas': users.pages,
        'pagina_atual': page
    }, 200

def obter_dados_dashboard():
    """Retorna estatísticas gerais para o dashboard"""
    total_usuarios = Usuario.query.count()
    total_campanhas = Campanha.query.count()
    campanhas_ativas = Campanha.query.filter_by(status='ativo').count()
    
    # Total de vendas (soma dos valores)
    total_vendas = db.session.query(func.sum(Compra.valor_total)).scalar() or 0
    
    # Vendas recentes (últimas 5)
    ultimas_vendas = Compra.query.order_by(Compra.criado_em.desc()).limit(5).all()
    
    return {
        'stats': {
            'total_usuarios': total_usuarios,
            'total_campanhas': total_campanhas,
            'campanhas_ativas': campanhas_ativas,
            'receita_total': float(total_vendas)
        },
        'ultimas_vendas': [{
            'id': v.public_id,
            'campanha': v.campanha.titulo,
            'usuario': v.usuario.nome,
            'valor': float(v.valor_total),
            'data': v.criado_em.isoformat()
        } for v in ultimas_vendas]
    }, 200


def obter_auditoria_campanha(campanha_id, page=1, per_page=20):
    """
    Retorna o histórico de AdminLog filtrado por campanha.

    Filtra entradas cujo campo `details` contenha o public_id ou id da campanha.
    Inclui todas as ações registradas para essa campanha (criação, atualização,
    definição de ganhador, etc.).

    Args:
        campanha_id: public_id (UUID) ou id interno da campanha
        page: Número da página
        per_page: Itens por página (máx. 50)

    Returns:
        tuple: (response dict, status code)
    """
    # Buscar campanha por public_id ou id interno
    campanha = Campanha.query.filter_by(public_id=campanha_id).first()
    if not campanha:
        try:
            campanha = Campanha.query.get(int(campanha_id))
        except (ValueError, TypeError):
            pass
    if not campanha:
        return {'erro': 'Campanha não encontrada'}, 404

    per_page = min(per_page, 50)

    # Filtra logs que referenciam esta campanha pelo public_id no campo details
    logs = AdminLog.query.filter(
        AdminLog.details.ilike(f'%{campanha.public_id}%')
    ).order_by(
        AdminLog.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return {
        'campanha_id': campanha.public_id,
        'campanha_titulo': campanha.titulo,
        'auditoria': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pagina': page,
        'por_pagina': per_page,
        'paginas': logs.pages,
    }, 200
