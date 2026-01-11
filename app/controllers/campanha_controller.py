"""
Controller de Campanhas
Contém a lógica de negócio para gerenciamento de campanhas
"""

from datetime import datetime
from app.models import db, Campanha, Usuario


def listar_campanhas(status=None, page=1, per_page=20):
    """
    Lista campanhas com paginação e filtros
    
    Args:
        status: Status da campanha (ativo, concluido, cancelado)
        page: Número da página
        per_page: Itens por página
    
    Returns:
        tuple: (response dict, status code)
    """
    query = Campanha.query
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Campanha.data_sorteio.desc())
    
    campanhas = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'campanhas': [c.to_dict(include_stats=True) for c in campanhas.items],
        'total': campanhas.total,
        'paginas': campanhas.pages,
        'pagina_atual': page
    }, 200


def obter_campanha_por_slug(slug):
    """
    Obtém detalhes de uma campanha pelo slug
    
    Args:
        slug: Slug da campanha
    
    Returns:
        tuple: (response dict, status code)
    """
    campanha = Campanha.query.filter_by(slug=slug).first()
    
    if not campanha:
        return {'erro': 'Campanha não encontrada'}, 404
    
    return campanha.to_dict(include_stats=True), 200


def criar_campanha(usuario_id, data):
    """
    Cria uma nova campanha (apenas administradores)
    
    Args:
        usuario_id: ID do usuário autenticado
        data: Dicionário com dados da campanha
    
    Returns:
        tuple: (response dict, status code)
    """
    try:
        # Converter de volta para inteiro (JWT retorna string)
        usuario = Usuario.query.get(int(usuario_id))
        
        if not usuario or not usuario.is_admin:
            return {'erro': 'Acesso negado'}, 403
        
        # Validação de campos obrigatórios
        if 'titulo' not in data: return {'erro': 'Título é obrigatório'}, 400
        
        # Gerar slug automaticamente se não fornecido
        slug = data.get('slug')
        if not slug:
            # Ex: "Iphone 15 Pro" -> "iphone-15-pro"
            import re
            import unicodedata
            
            # Normalizar para ASCII (remover acentos)
            nfkd_form = unicodedata.normalize('NFKD', data['titulo'])
            slug = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
            
            # Remover caracteres especiais e espaços
            slug = re.sub(r'[^a-zA-Z0-9\s-]', '', slug).lower().strip()
            slug = re.sub(r'[-\s]+', '-', slug)
            
        # Verificar se slug já existe
        if Campanha.query.filter_by(slug=slug).first():
             # Adicionar sufixo aleatório se já existir
             import random
             slug = f"{slug}-{random.randint(1000, 9999)}"

        # Criar nova campanha
        campanha = Campanha(
            titulo=data['titulo'],
            descricao=data.get('descricao'),
            slug=slug,
            imagem_principal=data.get('imagem_principal'),
            codigo=data.get('codigo'),
            tipo=data.get('tipo', 'regular'),
            premio=data.get('premio'),
            valor_titulo=data.get('valor_titulo'),
            total_titulos=data.get('total_titulos'),
            regulamento=data.get('regulamento')
        )

        # Tratamento robusto de datas
        if data.get('data_sorteio'):
            try:
                campanha.data_sorteio = datetime.fromisoformat(data['data_sorteio'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass # Mantém None se falhar

        if data.get('data_fim'):
            try:
                campanha.data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        
        db.session.add(campanha)
        db.session.commit()
        
        return {
            'mensagem': 'Campanha criada com sucesso',
            'campanha': campanha.to_dict()
        }, 201
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return {'erro': f'Erro ao criar campanha: {str(e)}'}, 500


def deletar_campanha(usuario_id, campanha_id):
    """
    Deleta uma campanha (apenas administradores)
    
    Args:
        usuario_id: ID do usuário admin
        campanha_id: ID da campanha a deletar
    
    Returns:
        tuple: (response dict, status code)
    """
    try:
        # Converter de volta para inteiro (JWT retorna string)
        usuario = Usuario.query.get(int(usuario_id))
        
        if not usuario or not usuario.is_admin:
            return {'erro': 'Acesso negado'}, 403
        
        # Buscar campanha
        campanha = Campanha.query.get(campanha_id)
        
        if not campanha:
            return {'erro': 'Campanha não encontrada'}, 404
        
        # Verificar se há compras associadas
        if campanha.compras.count() > 0:
            return {
                'erro': 'Não é possível deletar campanha com compras associadas',
                'sugestao': 'Considere alterar o status para "cancelado" ao invés de deletar'
            }, 400
        
        # Deletar campanha
        db.session.delete(campanha)
        db.session.commit()
        
        return {'mensagem': 'Campanha deletada com sucesso'}, 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return {'erro': f'Erro ao deletar campanha: {str(e)}'}, 500


def atualizar_campanha(usuario_id, campanha_id, data):
    """
    Atualiza uma campanha existente (apenas administradores)
    
    Args:
        usuario_id: ID do usuário admin
        campanha_id: ID da campanha a atualizar
        data: Dicionário com dados a atualizar
    
    Returns:
        tuple: (response dict, status code)
    """
    usuario = Usuario.query.get(int(usuario_id))
    
    if not usuario or not usuario.is_admin:
        return {'erro': 'Acesso negado'}, 403
    
    campanha = Campanha.query.get(campanha_id)
    
    if not campanha:
        return {'erro': 'Campanha não encontrada'}, 404
        
    # Atualizar campos se fornecidos
    if 'titulo' in data: campanha.titulo = data['titulo']
    if 'descricao' in data: campanha.descricao = data['descricao']
    if 'slug' in data: campanha.slug = data['slug']
    if 'imagem_principal' in data: campanha.imagem_principal = data['imagem_principal']
    if 'codigo' in data: campanha.codigo = data['codigo']
    if 'tipo' in data: campanha.tipo = data['tipo']
    if 'premio' in data: campanha.premio = data['premio']
    if 'valor_titulo' in data: campanha.valor_titulo = data['valor_titulo']
    if 'total_titulos' in data: campanha.total_titulos = data['total_titulos']
    if 'regulamento' in data: campanha.regulamento = data['regulamento']
    if 'status' in data: campanha.status = data['status']
    
    # Datas
    if 'data_sorteio' in data:
        # Tenta converter string ISO para datetime, lida com string vazia
        try:
            campanha.data_sorteio = datetime.fromisoformat(data['data_sorteio'].replace('Z', '+00:00')) if data['data_sorteio'] else None
        except (ValueError, TypeError):
            # Se falhar conversão (ex: formato diferente), ignora ou loga
            pass

    if 'data_fim' in data:
        try:
            campanha.data_fim = datetime.fromisoformat(data['data_fim'].replace('Z', '+00:00')) if data['data_fim'] else None
        except (ValueError, TypeError):
            pass
    
    db.session.commit()
    
    return {
        'mensagem': 'Campanha atualizada com sucesso',
        'campanha': campanha.to_dict()
    }, 200

