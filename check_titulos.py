"""
Script direto para verificar títulos vendidos
Execute: python check_titulos.py
"""

import sys
import os

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

# Importar depois de ajustar o path
from app import create_app
from app.models import Campanha, Compra, Titulo

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("   VERIFICAÇÃO DE TÍTULOS VENDIDOS")
    print("="*60 + "\n")
    
    # Campanhas
    campanhas = Campanha.query.all()
    print(f"📊 Total de campanhas: {len(campanhas)}\n")
    
    for c in campanhas:
        print(f"   Campanha: {c.titulo}")
        print(f"   - ID: {c.id}")
        print(f"   - Status: {c.status}")
        print(f"   - Total configurado: {c.total_titulos}")
        print(f"   - ★ Contador vendidos: {c.titulos_vendidos or 0}")
        
        # Contar títulos reais
        titulos_reais = Titulo.query.join(Compra).filter(
            Compra.campanha_id == c.id
        ).count()
        print(f"   - Títulos no banco: {titulos_reais}")
        
        # Contar compras
        compras_pendentes = Compra.query.filter_by(
            campanha_id=c.id,
            status_pagamento='pendente'
        ).count()
        
        compras_aprovadas = Compra.query.filter_by(
            campanha_id=c.id,
            status_pagamento='aprovado'
        ).count()
        
        print(f"   - Compras aprovadas: {compras_aprovadas}")
        print(f"   - Compras pendentes: {compras_pendentes}")
        print()
    
    # Verificar problema
    print("-"*60)
    compras_pendentes_total = Compra.query.filter_by(status_pagamento='pendente').count()
    
    if compras_pendentes_total > 0:
        print(f"\n⚠️  PROBLEMA ENCONTRADO:")
        print(f"   Você tem {compras_pendentes_total} compra(s) PENDENTE(s)!")
        print(f"\n💡 SOLUÇÃO:")
        print(f"   Execute: python aprovar_compras.py")
        print()
    else:
        print("\n✅ Todas as compras estão aprovadas!")
        
        # Verificar se contador está correto
        for c in campanhas:
            titulos_reais = Titulo.query.join(Compra).filter(
                Compra.campanha_id == c.id,
                Compra.status_pagamento == 'aprovado'
            ).count()
            
            if c.titulos_vendidos != titulos_reais:
                print(f"\n⚠️  Contador dessincronizado na campanha '{c.titulo}'")
                print(f"   Contador: {c.titulos_vendidos}, Real: {titulos_reais}")
    
    print("\n" + "="*60 + "\n")
