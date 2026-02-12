"""
Script para corrigir contador de títulos vendidos
Use quando aprovar compras manualmente pelo Beekeeper
"""

import sys
import os

# Add parent directory to Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from app import create_app
from app.models import db, Campanha, Compra

def corrigir_contadores():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("   CORREÇÃO DE CONTADORES DE TÍTULOS VENDIDOS")
        print("="*60 + "\n")
        
        campanhas = Campanha.query.all()
        
        if not campanhas:
            print("⚠️  Nenhuma campanha encontrada!")
            return
        
        print(f"📊 Encontradas {len(campanhas)} campanha(s):\n")
        
        for campanha in campanhas:
            # Contar títulos de compras APROVADAS
            total_aprovados = db.session.query(
                db.func.sum(Compra.quantidade_titulos)
            ).filter(
                Compra.campanha_id == campanha.id,
                Compra.status_pagamento == 'aprovado'
            ).scalar() or 0
            
            contador_antigo = campanha.titulos_vendidos or 0
            
            print(f"   Campanha: {campanha.titulo}")
            print(f"   - Contador atual: {contador_antigo}")
            print(f"   - Títulos aprovados (real): {total_aprovados}")
            
            if contador_antigo != total_aprovados:
                print(f"   - ⚠️  DIFERENÇA: {total_aprovados - contador_antigo}")
                campanha.titulos_vendidos = total_aprovados
                print(f"   - ✅ Corrigido para: {total_aprovados}")
            else:
                print(f"   - ✅ Já está correto!")
            
            print()
        
        # Perguntar confirmação
        resposta = input("Deseja salvar as correções? (s/n): ").strip().lower()
        
        if resposta == 's':
            db.session.commit()
            print("\n✅ Contadores corrigidos com sucesso!")
        else:
            print("\n❌ Operação cancelada. Nenhuma alteração foi salva.")
        
        print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    corrigir_contadores()
