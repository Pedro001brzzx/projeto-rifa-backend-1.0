"""
Script para aprovar manualmente compras pendentes.
Útil para testes e aprovações administrativas.
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from app import create_app
from app.models import db, Compra

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
        
        # Aprovar todas usando a função correta que GERA TÍTULOS
        from app.controllers.pagamento_controller import _aprovar_e_gerar_titulos
        
        aprovadas = 0
        erros = []
        
        for compra in compras_pendentes:
            try:
                # Esta função faz TUDO:
                # - Gera os títulos
                # - Incrementa contador da campanha
                # - Atualiza status para 'aprovado'
                # - Define data_pagamento
                _aprovar_e_gerar_titulos(compra)
                aprovadas += 1
            except Exception as e:
                erros.append(f"Compra #{compra.id}: {str(e)}")
                print(f"❌ Erro ao aprovar compra #{compra.id}: {str(e)}")
        
        if erros:
            print(f'\n⚠️ Algumas compras falharam:')
            for erro in erros:
                print(f'  - {erro}')
        
        print(f'\n✅ {aprovadas} compra(s) aprovada(s) com sucesso!')
        print('🎫 Títulos gerados automaticamente!')
        print('\nAgora você pode testar a rota /api/meus-titulos!')

if __name__ == '__main__':
    aprovar_compras()
