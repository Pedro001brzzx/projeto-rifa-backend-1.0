"""
Job de limpeza de compras expiradas
Cancela compras pendentes que ultrapassaram o prazo de 10 minutos
"""

from datetime import datetime
from sqlalchemy import or_
from app.models import db, Compra, Titulo


def cancelar_compras_expiradas():
    """
    Cancela compras pendentes que passaram do prazo de expiração.
    Libera os títulos reservados e atualiza o contador da campanha.
    
    OTIMIZAÇÕES v2:
    - Query SQL direta com filtro de expiração
    - Transação individual por compra (rollback isolado)
    - Logging detalhado com timestamps
    
    Returns:
        int: Número de compras canceladas
    """
    from datetime import datetime
    
    now = datetime.utcnow()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"\n🧹 [{timestamp}] Iniciando limpeza de compras expiradas...")
    
    # OTIMIZAÇÃO: Query SQL direta com filtro de expiração no banco
    # Busca compras pendentes que:
    # 1. Não têm expira_em (antigas, NULL) OU
    # 2. Têm expira_em expirado (< agora)
    compras_expiradas = Compra.query.filter(
        Compra.status_pagamento == 'pendente',
        or_(
            Compra.expira_em == None,  # Compras antigas sem campo
            Compra.expira_em < now      # Compras expiradas
        )
    ).all()
    
    if not compras_expiradas:
        print(f"✅ [{timestamp}] Nenhuma compra expirada encontrada")
        return 0
    
    print(f"📊 [{timestamp}] Encontradas {len(compras_expiradas)} compra(s) expirada(s)")
    
    compras_canceladas = 0
    titulos_liberados_total = 0
    
    # OTIMIZAÇÃO: Processar cada compra em transação separada
    for compra in compras_expiradas:
        try:
            # Deletar títulos reservados
            titulos_count = Titulo.query.filter_by(compra_id=compra.id).count()
            Titulo.query.filter_by(compra_id=compra.id).delete()
            
            # Decrementar contador de títulos vendidos da campanha
            if compra.campanha and compra.campanha.status == 'ativo':
                compra.campanha.titulos_vendidos = max(
                    0, 
                    compra.campanha.titulos_vendidos - compra.quantidade_titulos
                )
            
            # Marcar compra como expirada
            compra.status_pagamento = 'expirado'
            
            # Commit individual (rollback isolado em caso de erro)
            db.session.commit()
            
            compras_canceladas += 1
            titulos_liberados_total += titulos_count
            
            # Logging detalhado
            expira_info = f"expirou em {compra.expira_em.strftime('%H:%M:%S')}" if compra.expira_em else "sem expira_em (antiga)"
            print(f"   ✅ Compra #{compra.id} - {titulos_count} títulos liberados ({expira_info})")
            
        except Exception as e:
            # Rollback desta compra específica
            db.session.rollback()
            print(f"   ❌ Erro ao cancelar compra #{compra.id}: {str(e)}")
            # Continua processando outras compras
            continue
    
    # Relatório final
    timestamp_final = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n📋 [{timestamp_final}] Resumo da limpeza:")
    print(f"   • Compras canceladas: {compras_canceladas}")
    print(f"   • Títulos liberados: {titulos_liberados_total}")
    print(f"   • Tempo de processamento: {(datetime.utcnow() - now).total_seconds():.2f}s\n")
    
    return compras_canceladas


if __name__ == '__main__':
    # Permite executar este script standalone
    from app import create_app
    
    app = create_app()
    with app.app_context():
        canceladas = cancelar_compras_expiradas()
        print(f"Total de compras canceladas: {canceladas}")
