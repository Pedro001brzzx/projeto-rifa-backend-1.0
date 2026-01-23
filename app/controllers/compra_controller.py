"""
Controller de Compras
Contém a lógica de negócio para compras e geração de títulos
"""

import random
from app.models import db, Campanha, Compra, Titulo

# Constante: Número máximo de títulos únicos possíveis
# Formato 0XXXXX permite números de 000000 a 099999
MAX_TITULOS_POSSIVEIS = 100000


def criar_compra(usuario_id, data):
    """
    Cria uma nova compra de títulos
    
    Args:
        usuario_id: ID do usuário autenticado
        data: Dicionário com dados da compra
    
    Returns:
        tuple: (response dict, status code)
    """
    campanha = Campanha.query.get(data['campanha_id'])
    if not campanha:
        return {'erro': 'Campanha não encontrada'}, 404
    
    if campanha.status != 'ativo':
        return {'erro': 'Campanha não está ativa'}, 400
    
    quantidade = data['quantidade_titulos']
    
    # Contar títulos já vendidos (aprovados) desta campanha
    # OTIMIZADO: Query direta sem JOIN (usa índice idx_titulo_campanha)
    titulos_ja_vendidos = Titulo.query.filter(
        Titulo.campanha_id == campanha.id
    ).count()
    
    # Validação 1: Verificar limite físico do sistema (máximo 100k números únicos)
    if titulos_ja_vendidos + quantidade > MAX_TITULOS_POSSIVEIS:
        disponiveis = MAX_TITULOS_POSSIVEIS - titulos_ja_vendidos
        return {
            'erro': f'Limite máximo de títulos atingido. Apenas {disponiveis} título(s) disponível(is) para esta campanha.',
            'titulos_disponiveis': disponiveis,
            'limite_maximo': MAX_TITULOS_POSSIVEIS
        }, 400
    
    # Validação 2: Verificar limite configurado da campanha
    titulos_disponiveis = campanha.total_titulos - campanha.titulos_vendidos
    if quantidade > titulos_disponiveis:
        return {
            'erro': f'Quantidade indisponível. Esta campanha tem {titulos_disponiveis} título(s) disponível(is).',
            'titulos_disponiveis': titulos_disponiveis
        }, 400
    
    valor_total = float(campanha.valor_titulo) * quantidade
    
    # Criar compra (converter usuario_id para int)
    compra = Compra(
        usuario_id=int(usuario_id),
        campanha_id=campanha.id,
        quantidade_titulos=quantidade,
        valor_total=valor_total,
        metodo_pagamento=data.get('metodo_pagamento', 'pix')
    )
    
    # Definir prazo de expiração (10 minutos)
    from datetime import datetime, timedelta
    compra.expira_em = datetime.utcnow() + timedelta(minutes=10)
    
    db.session.add(compra)
    db.session.flush()
    
    # Gerar títulos
    gerar_titulos(compra.id, campanha.id, quantidade)
    
    db.session.commit()
    
    return {
        'mensagem': 'Compra realizada com sucesso',
        'compra': compra.to_dict()
    }, 201


def gerar_titulos(compra_id, campanha_id, quantidade):
    """
    Gera números de títulos únicos para uma compra (OTIMIZADO)
    Formato: 0XXXXX (6 dígitos, sempre começando com 0)
    Exemplos: 000001, 054398, 099999
    
    OTIMIZAÇÕES:
    - Cache em memória: busca números usados UMA vez, depois usa set (instantâneo)
    - Bulk insert: adiciona todos os títulos de uma vez ao banco
    - Query direta: usa campanha_id sem JOIN
    
    Args:
        compra_id: ID da compra
        campanha_id: ID da campanha
        quantidade: Quantidade de títulos a gerar
    
    Raises:
        Exception: Se não conseguir gerar números únicos (limite esgotado)
    """
    MAX_TENTATIVAS = 1000  # Previne loop infinito
    
    # OTIMIZAÇÃO 1: Buscar TODOS os números usados desta campanha UMA vez
    # Usa set para verificação O(1) em vez de query O(n) a cada tentativa
    numeros_usados_query = Titulo.query.filter(
        Titulo.campanha_id == campanha_id
    ).with_entities(Titulo.numero).all()
    
    numeros_usados = set(numero for (numero,) in numeros_usados_query)
    
    # OTIMIZAÇÃO 2: Gerar todos os números em memória primeiro
    titulos_para_inserir = []
    
    for i in range(quantidade):
        tentativas = 0
        numero_gerado = False
        
        # Gerar número único de título (0 a 99999, formatado como 0XXXXX)
        while tentativas < MAX_TENTATIVAS:
            # Gera número de 0 a 99999
            numero_aleatorio = random.randint(0, 99999)
            # Formata com 6 dígitos, preenchendo com zeros à esquerda (0XXXXX)
            numero = f"{numero_aleatorio:06d}"
            
            # Verifica no set em memória (instantâneo) em vez de query ao banco
            if numero not in numeros_usados:
                numeros_usados.add(numero)  # Adiciona ao cache
                numero_gerado = True
                break
            
            tentativas += 1
        
        # Se não conseguiu gerar após MAX_TENTATIVAS, provavelmente esgotou números
        if not numero_gerado:
            titulos_gerados = i
            raise Exception(
                f'Não foi possível gerar todos os títulos. '
                f'Números disponíveis esgotados após {titulos_gerados} título(s). '
                f'Campanha atingiu limite máximo de {MAX_TITULOS_POSSIVEIS} títulos únicos.'
            )
        
        # Adiciona à lista para bulk insert
        titulos_para_inserir.append(
            Titulo(
                compra_id=compra_id,
                campanha_id=campanha_id,  # Novo campo para performance
                numero=numero
            )
        )
    
    # OTIMIZAÇÃO 3: Bulk insert - adiciona todos de uma vez
    db.session.bulk_save_objects(titulos_para_inserir)


def listar_compras_usuario(usuario_id, page=1, per_page=20):
    """
    Lista as compras aprovadas de um usuário
    
    Args:
        usuario_id: ID do usuário
        page: Número da página
        per_page: Itens por página
    
    Returns:
        tuple: (response dict, status code)
    """
    compras = Compra.query.filter_by(
        usuario_id=int(usuario_id),
        status_pagamento='aprovado'
    ).order_by(Compra.criado_em.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return {
        'compras': [c.to_dict() for c in compras.items],
        'total': compras.total,
        'paginas': compras.pages,
        'pagina_atual': page
    }, 200


def deletar_compra(usuario_id, compra_id):
    """
    Deleta uma compra e seus títulos associados (apenas administradores)
    
    Args:
        usuario_id: ID do usuário admin
        compra_id: ID da compra a deletar
    
    Returns:
        tuple: (response dict, status code)
    """
    from app.models import Usuario
    
    # Verificar se usuário é admin
    usuario = Usuario.query.get(int(usuario_id))
    if not usuario or not usuario.is_admin:
        return {'erro': 'Acesso negado'}, 403
    
    # Buscar compra
    compra = Compra.query.get(compra_id)
    
    if not compra:
        return {'erro': 'Compra não encontrada'}, 404
    
    # Verificar se a campanha já foi sorteada/concluída
    if compra.campanha.status == 'concluido':
        return {
            'erro': 'Não é possível deletar compra de campanha já concluída',
            'sugestao': 'Campanhas concluídas são mantidas para histórico'
        }, 400
    
    # Contar títulos a serem deletados
    qtd_titulos = Titulo.query.filter_by(compra_id=compra_id).count()
    
    # Deletar títulos associados primeiro (cascade)
    Titulo.query.filter_by(compra_id=compra_id).delete()
    
    # Deletar compra
    db.session.delete(compra)
    db.session.commit()
    
    return {
        'mensagem': 'Compra deletada com sucesso',
        'titulos_deletados': qtd_titulos
    }, 200

