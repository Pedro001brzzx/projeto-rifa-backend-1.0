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


def listar_comunicados(page=1, per_page=10):
    """
    Lista comunicados ativos com paginação.

    Args:
        page: Número da página
        per_page: Itens por página (máx. 50)

    Returns:
        tuple: (response dict, status code)
    """
    per_page = min(per_page, 50)
    paginado = Comunicado.query.filter_by(ativo=True).order_by(
        Comunicado.criado_em.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return {
        'comunicados': [c.to_dict() for c in paginado.items],
        'total': paginado.total,
        'pagina': page,
        'por_pagina': per_page,
        'paginas': paginado.pages,
    }, 200


def criar_comunicado(data):
    """
    Cria um novo comunicado
    
    Args:
        data: Dicionário com titulo, conteudo, tipo (opcional)
    
    Returns:
        tuple: (response dict, status code)
    """
    comunicado = Comunicado(
        titulo=data['titulo'],
        conteudo=data['conteudo'],
        tipo=data.get('tipo', 'informativo'),
        ativo=data.get('ativo', True)
    )
    
    db.session.add(comunicado)
    db.session.commit()
    
    return {'mensagem': 'Comunicado criado com sucesso', 'comunicado': comunicado.to_dict()}, 201


def atualizar_comunicado(comunicado_id, data):
    """
    Atualiza um comunicado existente
    
    Args:
        comunicado_id: ID do comunicado
        data: Dicionário com campos a atualizar
    
    Returns:
        tuple: (response dict, status code)
    """
    comunicado = db.session.get(Comunicado, comunicado_id)
    if not comunicado:
        return {'erro': 'Comunicado não encontrado'}, 404
    
    if 'titulo' in data:
        comunicado.titulo = data['titulo']
    if 'conteudo' in data:
        comunicado.conteudo = data['conteudo']
    if 'tipo' in data:
        comunicado.tipo = data['tipo']
    if 'ativo' in data:
        comunicado.ativo = data['ativo']
    
    db.session.commit()
    
    return {'mensagem': 'Comunicado atualizado', 'comunicado': comunicado.to_dict()}, 200


def deletar_comunicado(comunicado_id):
    """
    Deleta um comunicado
    
    Args:
        comunicado_id: ID do comunicado
    
    Returns:
        tuple: (response dict, status code)
    """
    comunicado = db.session.get(Comunicado, comunicado_id)
    if not comunicado:
        return {'erro': 'Comunicado não encontrado'}, 404
    
    db.session.delete(comunicado)
    db.session.commit()
    
    return {'mensagem': 'Comunicado excluído com sucesso'}, 200


def enviar_contato(data):
    """
    Registra uma mensagem de contato
    
    Args:
        data: Dicionário com dados do contato
    
    Returns:
        tuple: (response dict, status code)
    """
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
