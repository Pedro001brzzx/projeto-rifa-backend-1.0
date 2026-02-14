"""
Controller de Compras
Contém a lógica de negócio para compras e geração de títulos
"""

import random
import requests
import os
from app.models import db, Campanha, Compra, Titulo

# Constante: Número máximo de títulos únicos possíveis
# Formato 0XXXXX permite números de 000000 a 099999
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
    
    # Validar limites de quantidade da campanha
    if quantidade < campanha.min_quantidade_compra:
        return {
            'erro': f'Quantidade mínima: {campanha.min_quantidade_compra} títulos',
            'min_quantidade': campanha.min_quantidade_compra
        }, 400
    
    if campanha.max_quantidade_compra and quantidade > campanha.max_quantidade_compra:
        return {
            'erro': f'Quantidade máxima: {campanha.max_quantidade_compra} títulos',
            'max_quantidade': campanha.max_quantidade_compra
        }, 400
    
    # ✅ VALIDAÇÃO DE DISPONIBILIDADE
    # Verificar se a quantidade solicitada está disponível
    titulos_disponiveis = campanha.total_titulos - campanha.titulos_vendidos
    if quantidade > titulos_disponiveis:
        return {
            'erro': f'Quantidade indisponível. Restam apenas alguns títulos.', # Mensagem vaga para o usuário
            'titulos_disponiveis': titulos_disponiveis # Para o frontend atualizar se necessário
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
    
    # IMPORTANTE: Definir prazo de expiração (10 minutos) ANTES de adicionar ao session
    from datetime import datetime, timedelta
    expiracao = datetime.utcnow() + timedelta(minutes=10)
    compra.expira_em = expiracao
    
    print(f"🕐 [DEBUG] Compra criada com expira_em: {expiracao.isoformat()}")
    
    db.session.add(compra)
    db.session.flush()  # Gera ID da compra
    
    print(f"✅ [DEBUG] Compra #{compra.id} adicionada ao session")
    
    # ⚠️ IMPORTANTE: NÃO gerar títulos aqui!
    # Títulos serão gerados APENAS após aprovação do pagamento
    # Isso evita reservar números desnecessariamente
    
    db.session.commit()
    
    print(f"💾 [DEBUG] Compra #{compra.id} criada SEM títulos (aguardando pagamento)")
    
    # Gerar PIX QR Code se método for PIX
    dados_pix = None
    # ⚠️ FIX: NÃO gerar PIX aqui!
    # O pagamento agora é gerenciado exclusivamente pelo pagamento_controller._gerar_dados_pagamento
    # if compra.metodo_pagamento == 'pix':
    #     try:
    #         dados_pix = criar_pix_qrcode(compra)
    #         if dados_pix:
    #             # Salvar dados do PIX no banco para consulta posterior
    #             compra.pix_copia_cola = dados_pix['pix_copia_cola']
    #             compra.pix_qr_code_base64 = dados_pix['qrcode_base64']
    #             compra.transacao_id = dados_pix['pix_id']
    #             db.session.commit()
    #             print(f"✅ [DEBUG] PIX gerado e salvo para compra #{compra.id}")
    #     except Exception as e:
    #         print(f"❌ [ERRO] Falha ao gerar PIX: {str(e)}")
    
    response_data = {
        'mensagem': 'Compra realizada com sucesso',
        'compra': compra.to_dict()
    }
    
    # Adicionar dados do PIX à resposta
    if dados_pix:
        response_data.update(dados_pix)
    
    return response_data, 201


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
        
        # Gerar número único de título (000000 a 099999, sem zeros à esquerda)
        while tentativas < MAX_TENTATIVAS:
            # Gera número de 000000 a 099999 (5 dígitos, formatados com 6)
            numero_int = random.randint(0, 99999)
            numero = f"{numero_int:06d}"
            
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
    Lista TODAS as compras de um usuário (aprovadas, pendentes, expiradas)
    
    IMPORTANTE: Compras pendentes aparecem no TOPO para visibilidade
    
    Args:
        usuario_id: ID do usuário
        page: Número da página
        per_page: Itens por página
    
    Returns:
        tuple: (response dict, status code)
    """
    from sqlalchemy import case, and_, or_
    from datetime import datetime
    
    # Data atual para verificar expiração em tempo real
    now = datetime.utcnow()
    
    # Ordenação Inteligente (Frontend Friendly)
    # 1. PENDENTES VÁLIDOS (Topo da lista): Status pendente E data de expiração no futuro
    # 2. APROVADOS (Meio): Compras pagas
    # 3. EXPIRADOS/OUTROS (Fim): Status expirado OU (pendente mas já passou da data)
    
    status_priority = case(
        (and_(Compra.status_pagamento == 'pendente', Compra.expira_em > now), 1),
        (Compra.status_pagamento == 'aprovado', 2),
        (or_(Compra.status_pagamento == 'expirado', Compra.status_pagamento == 'cancelado'), 3),
        else_=3 # Pendentes vencidos caem aqui também
    )
    
    compras = Compra.query.filter_by(
        usuario_id=int(usuario_id)
    ).order_by(
        status_priority.asc(),           # Prioridade calculada
        Compra.criado_em.desc()          # Mais recentes primeiro dentro do grupo
    ).paginate(
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

