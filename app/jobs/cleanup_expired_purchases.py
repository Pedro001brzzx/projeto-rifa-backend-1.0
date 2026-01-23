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
    
    Returns:
        int: Número de compras canceladas
    """
    now = datetime.utcnow()
    
    # Buscar TODAS as compras pendentes
    # Filtraremos em Python para evitar erro de atributo
    todas_pendentes = Compra.query.filter(
        Compra.status_pagamento == 'pendente'
    ).all()
    
    # Filtrar manualmente as expiradas
    compras_expiradas = []
    for compra in todas_pendentes:
        # Compras sem expira_em (antigas) OU com expira_em expirado
        if not hasattr(compra, 'expira_em') or compra.expira_em is None or compra.expira_em < now:
            compras_expiradas.append(compra)
    
    compras_canceladas = 0
    
    for compra in compras_expiradas:
        try:
            # Deletar títulos reservados (cascade vai fazer isso automaticamente)
            # Mas vamos fazer explícito para ter controle
            titulos_count = Titulo.query.filter_by(compra_id=compra.id).count()
            Titulo.query.filter_by(compra_id=compra.id).delete()
            
            # Decrementar contador de títulos vendidos da campanha
            # (somente se a campanha não foi concluída)
            if compra.campanha and compra.campanha.status == 'ativo':
                compra.campanha.titulos_vendidos = max(
                    0, 
                    compra.campanha.titulos_vendidos - compra.quantidade_titulos
                )
            
            # Marcar compra como expirada
            compra.status_pagamento = 'expirado'
            
            compras_canceladas += 1
            
            print(f"✅ Compra #{compra.id} expirada - {titulos_count} títulos liberados")
            
        except Exception as e:
            print(f"❌ Erro ao cancelar compra #{compra.id}: {str(e)}")
            # Continua processando outras compras mesmo se uma falhar
            continue
    
    # Commit de todas as alterações
    db.session.commit()
    
    if compras_canceladas > 0:
        print(f"🧹 {compras_canceladas} compra(s) expirada(s) foram canceladas")
    
    return compras_canceladas


if __name__ == '__main__':
    # Permite executar este script standalone
    from app import create_app
    
    app = create_app()
    with app.app_context():
        canceladas = cancelar_compras_expiradas()
        print(f"Total de compras canceladas: {canceladas}")
