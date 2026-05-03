"""
Controller de Campanhas
Contém a lógica de negócio para gerenciamento de campanhas
"""

from datetime import datetime, date
from app.models import db, Campanha, Usuario, TituloPremiado
from app.models.compra import Compra
from app.models.titulo import Titulo
import uuid


def _buscar_campanha_por_id(campanha_id):
    """Busca campanha por public_id (UUID) ou id interno (int)"""
    campanha = Campanha.query.filter_by(public_id=campanha_id).first()
    if not campanha:
        try:
            campanha = db.session.get(Campanha, int(campanha_id))
        except (ValueError, TypeError):
            pass
    return campanha


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
    
    query = query.order_by(Campanha.criado_em.desc())
    
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
        usuario = db.session.get(Usuario, int(usuario_id))
        
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
            public_id=str(uuid.uuid4()),
            descricao=data.get('descricao'),
            slug=slug,
            imagem_principal=data.get('imagem_principal'),
            codigo=data.get('codigo'),
            tipo=data.get('tipo', 'regular'),
            premio=data.get('premio'),
            valor_titulo=data.get('valor_titulo'),
            total_titulos=data.get('total_titulos'),
            min_quantidade_compra=data.get('min_quantidade_compra', 1),
            max_quantidade_compra=data.get('max_quantidade_compra'),
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
        usuario = db.session.get(Usuario, int(usuario_id))
        
        if not usuario or not usuario.is_admin:
            return {'erro': 'Acesso negado'}, 403
        
        # Buscar campanha
        campanha = _buscar_campanha_por_id(campanha_id)
        
        if not campanha:
            return {'erro': 'Campanha não encontrada'}, 404
        
        # Excluir Títulos Premiados associados
        TituloPremiado.query.filter_by(campanha_id=campanha.id).delete()
        
        # Excluir Títulos associados
        Titulo.query.filter_by(campanha_id=campanha.id).delete()
        
        # Excluir Compras associadas
        Compra.query.filter_by(campanha_id=campanha.id).delete()
        
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
    usuario = db.session.get(Usuario, int(usuario_id))
    
    if not usuario or not usuario.is_admin:
        return {'erro': 'Acesso negado'}, 403
    
    campanha = _buscar_campanha_por_id(campanha_id)
    
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
    if 'min_quantidade_compra' in data: campanha.min_quantidade_compra = data['min_quantidade_compra']
    if 'max_quantidade_compra' in data: campanha.max_quantidade_compra = data['max_quantidade_compra']
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

def listar_titulos_premiados(slug):
    """
    Lista os títulos premiados de uma campanha pelo slug,
    incluindo automaticamente o dono de cada número (se existir).
    """
    campanha = Campanha.query.filter_by(slug=slug).first()
    
    if not campanha:
        return {'erro': 'Campanha não encontrada'}, 404
        
    titulos = TituloPremiado.query.filter_by(campanha_id=campanha.id).all()
    
    # Pré-carregar donos: dict { numero -> { compra_id, titulo_id, nome, telefone } }
    numeros = [t.numero_titulo for t in titulos]
    donos = {}
    
    if numeros:
        resultados = db.session.query(
            Titulo, Compra, Usuario
        ).join(
            Compra, Titulo.compra_id == Compra.id
        ).join(
            Usuario, Compra.usuario_id == Usuario.id
        ).filter(
            Titulo.campanha_id == campanha.id,
            Titulo.numero.in_(numeros),
            Compra.status_pagamento == 'aprovado'
        ).all()

        for titulo_obj, compra_obj, usuario_obj in resultados:
            donos[titulo_obj.numero] = {
                'compra_id': compra_obj.id,
                'titulo_id': titulo_obj.id,
                'usuario_id': usuario_obj.id,
                'nome': usuario_obj.nome,
                'telefone': usuario_obj.telefone,
            }

    titulos_data = []
    for t in titulos:
        d = t.to_dict()
        dono = donos.get(t.numero_titulo)
        if dono:
            d['dono'] = dono
        else:
            d['dono'] = None
        titulos_data.append(d)
    
    return {
        'titulos_premiados': titulos_data,
        'total': len(titulos_data),
        'ganhos': sum(1 for t in titulos_data if t['status'] == 'ganho'),
        'disponiveis': sum(1 for t in titulos_data if t['status'] == 'disponivel')
    }, 200



def adicionar_titulo_premiado(campanha_id, data):
    """
    Adiciona um título premiado a uma campanha (admin only)
    campanha_id pode ser o public_id (UUID) ou slug
    """
    campanha = Campanha.query.filter_by(public_id=campanha_id).first()
    if not campanha:
        # Fallback: tentar buscar por id inteiro
        try:
            campanha = db.session.get(Campanha, int(campanha_id))
        except (ValueError, TypeError):
            pass
    if not campanha:
        return {'erro': 'Campanha não encontrada'}, 404

    if not data.get('numero_titulo') or not data.get('valor_premio'):
        return {'erro': 'Número do título e valor do prêmio são obrigatórios'}, 400

    titulo = TituloPremiado(
        campanha_id=campanha.id,
        numero_titulo=data['numero_titulo'],
        valor_premio=data['valor_premio'],
        status='disponivel'
    )

    db.session.add(titulo)
    db.session.commit()

    return {'mensagem': 'Título premiado adicionado', 'titulo': titulo.to_dict()}, 201


def deletar_titulo_premiado(titulo_id):
    """
    Deleta um título premiado (admin only)
    """
    titulo = db.session.get(TituloPremiado, titulo_id)
    if not titulo:
        return {'erro': 'Título premiado não encontrado'}, 404

    db.session.delete(titulo)
    db.session.commit()

    return {'mensagem': 'Título premiado removido'}, 200


def buscar_compradores(campanha_id, termo):
    """
    Busca compradores de uma campanha por nome, telefone ou número de cota
    """
    campanha = _buscar_campanha_por_id(campanha_id)
    if not campanha:
        return {'erro': 'Campanha não encontrada'}, 404

    # Buscar titulos desta campanha com compras aprovadas
    query = db.session.query(
        Titulo, Compra, Usuario
    ).join(
        Compra, Titulo.compra_id == Compra.id
    ).join(
        Usuario, Compra.usuario_id == Usuario.id
    ).filter(
        Titulo.campanha_id == campanha.id,
        Compra.status_pagamento == 'aprovado'
    )

    # Filtrar pelo termo de busca
    if termo:
        search_digits = ''.join(filter(str.isdigit, termo))
        search = f'%{termo}%'
        
        # Cria condições OR
        condicoes = [
            Usuario.nome.ilike(search),
            Titulo.numero.ilike(search)
        ]
        
        if search_digits:
             # Se for puramente números, checar telefone e cota
             search_digits_like = f'%{search_digits}%'
             # SQLite replace manual
             telefone_limpo = db.func.replace(db.func.replace(db.func.replace(db.func.replace(Usuario.telefone, '(', ''), ')', ''), '-', ''), ' ', '')
             condicoes.append(telefone_limpo.like(search_digits_like))
             condicoes.append(Titulo.numero.ilike(search_digits_like))
             # Checar também a cota com zero padding se for puramente número
             condicoes.append(Titulo.numero == search_digits.zfill(6))
             
        query = query.filter(db.or_(*condicoes))

    results = query.limit(50).all()

    compradores = []
    for titulo, compra, usuario in results:
        compradores.append({
            'compra_id': compra.id,
            'titulo_id': titulo.id,
            'usuario_id': usuario.id,
            'nome': usuario.nome,
            'telefone': usuario.telefone,
            'numero_titulo': titulo.numero,
            'data_compra': compra.criado_em.isoformat() + 'Z' if compra.criado_em else None
        })

    return {'compradores': compradores, 'total': len(compradores)}, 200


def definir_ganhador(campanha_id, data):
    """
    Define o ganhador de uma campanha
    """
    from app.utils.admin_logger import log_admin_action

    campanha = _buscar_campanha_por_id(campanha_id)
    if not campanha:
        return {'erro': 'Campanha não encontrada'}, 404

    compra_id = data.get('compra_id')
    titulo_id = data.get('titulo_id')
    metodo = data.get('metodo', 'manual')

    if not compra_id:
        return {'erro': 'ID da compra é obrigatório'}, 400

    compra = db.session.get(Compra, compra_id)
    if not compra:
        return {'erro': 'Compra não encontrada'}, 404

    # Definir ganhador na campanha
    campanha.ganhador_id = compra.usuario_id
    campanha.status = 'concluido'
    campanha.data_conclusao = date.today()
    campanha.sorteio_metodo = metodo

    # Marcar titulo como ganhador se fornecido
    if titulo_id:
        titulo = db.session.get(Titulo, titulo_id)
        if titulo:
            titulo.is_ganhador = True
            campanha.numero_sorteado = titulo.numero

    db.session.commit()

    log_admin_action(
        'Definição de Ganhador',
        details=(
            f"campanha_id={campanha.public_id} | campanha='{campanha.titulo}' | "
            f"ganhador_id={compra.usuario_id} | ganhador='{compra.usuario.nome}' | "
            f"numero_sorteado={campanha.numero_sorteado} | metodo={metodo}"
        ),
    )

    return {
        'mensagem': 'Ganhador definido com sucesso',
        'ganhador': {
            'nome': compra.usuario.nome,
            'campanha': campanha.titulo,
            'numero_sorteado': campanha.numero_sorteado,
            'metodo': metodo,
        }
    }, 200
