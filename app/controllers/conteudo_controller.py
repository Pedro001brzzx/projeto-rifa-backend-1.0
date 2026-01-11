"""
Controller de Conteúdo
Contém a lógica de negócio para artigos, comunicados e contatos
"""

from app.models import db, Artigo, Comunicado, Contato


def listar_artigos(page=1, per_page=10):
    """
    Lista artigos publicados
    
    Args:
        page: Número da página
        per_page: Itens por página
    
    Returns:
        tuple: (response dict, status code)
    """
    artigos = Artigo.query.filter_by(publicado=True).order_by(
        Artigo.criado_em.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'artigos': [a.to_dict() for a in artigos.items],
        'total': artigos.total,
        'paginas': artigos.pages
    }, 200


def obter_artigo(slug):
    """
    Obtém detalhes de um artigo pelo slug
    
    Args:
        slug: Slug do artigo
    
    Returns:
        tuple: (response dict, status code)
    """
    artigo = Artigo.query.filter_by(slug=slug, publicado=True).first()
    
    if not artigo:
        return {'erro': 'Artigo não encontrado'}, 404
    
    return artigo.to_dict(), 200


def listar_comunicados():
    """
    Lista comunicados ativos (últimos 10)
    
    Returns:
        tuple: (response dict, status code)
    """
    comunicados = Comunicado.query.filter_by(ativo=True).order_by(
        Comunicado.criado_em.desc()
    ).limit(10).all()
    
    return {
        'comunicados': [c.to_dict() for c in comunicados]
    }, 200


def enviar_contato(data):
    """
    Registra uma mensagem de contato
    
    Args:
        data: Dicionário com dados do contato
    
    Returns:
        tuple: (response dict, status code)
    """
    if not data.get('nome') or not data.get('email') or not data.get('mensagem'):
        return {'erro': 'Nome, email e mensagem são obrigatórios'}, 400
    
    contato = Contato(
        nome=data['nome'],
        email=data['email'],
        telefone=data.get('telefone'),
        assunto=data.get('assunto'),
        mensagem=data['mensagem']
    )
    
    db.session.add(contato)
    db.session.commit()
    
    return {'mensagem': 'Mensagem enviada com sucesso'}, 201
