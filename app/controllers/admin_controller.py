"""
Controller Administrativo
Contém lógica para funcionalidades exclusivas de administradores
"""

from app.models import db, Usuario, Compra, Campanha
from sqlalchemy import func

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
