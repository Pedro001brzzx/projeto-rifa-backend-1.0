"""
Script para aprovar compras pendentes
Execute: python aprovar_compras.py
"""

from app import create_app
from app.models import db, Compra
from datetime import datetime

def aprovar_compras():
    app = create_app()
    
    with app.app_context():
        # Buscar todas as compras pendentes
        compras_pendentes = Compra.query.filter_by(status_pagamento='pendente').all()
        
        if not compras_pendentes:
            print('ℹ️  Nenhuma compra pendente encontrada.')
            print('\nCompras no sistema:')
            todas_compras = Compra.query.all()
            for c in todas_compras:
                status_emoji = '✅' if c.status_pagamento == 'aprovado' else '⏳'
                print(f'  {status_emoji} Compra #{c.id} - {c.quantidade_titulos} títulos - {c.status_pagamento}')
            return
        
        print(f'📋 Encontradas {len(compras_pendentes)} compra(s) pendente(s):\n')
        
        # Listar compras pendentes
        for compra in compras_pendentes:
            print(f'  ⏳ Compra #{compra.id}')
            print(f'     Usuário: {compra.usuario.nome}')
            print(f'     Campanha: {compra.campanha.titulo}')
            print(f'     Títulos: {compra.quantidade_titulos}')
            print(f'     Valor: R$ {compra.valor_total}')
            print(f'     Método: {compra.metodo_pagamento}')
            print()
        
        # Perguntar confirmação
        resposta = input('Deseja aprovar todas essas compras? (s/n): ').strip().lower()
        
        if resposta != 's':
            print('❌ Operação cancelada.')
            return
        
        # Aprovar todas
        for compra in compras_pendentes:
            compra.status_pagamento = 'aprovado'
            compra.data_pagamento = datetime.utcnow()
            
            # Atualizar contador de títulos vendidos na campanha
            campanha = compra.campanha
            if campanha:
                campanha.titulos_vendidos = (campanha.titulos_vendidos or 0) + compra.quantidade_titulos
        
        db.session.commit()
        
        print(f'\n✅ {len(compras_pendentes)} compra(s) aprovada(s) com sucesso!')
        print('💡 Contadores de títulos vendidos atualizados nas campanhas!')
        print('\nAgora você pode testar a rota /api/meus-titulos!')

if __name__ == '__main__':
    aprovar_compras()
