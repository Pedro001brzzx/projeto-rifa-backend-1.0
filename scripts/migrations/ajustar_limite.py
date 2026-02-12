"""
Script para ajustar total_titulos da campanha quando ultrapassar o limite
"""

import sys
import os

# Add project root to Python path (2 levels up)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from app import create_app
from app.models import db, Campanha

def ajustar_limite_campanha():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("   AJUSTE DE LIMITE DE CAMPANHAS")
        print("="*60 + "\n")
        
        campanhas = Campanha.query.all()
        
        campanhas_com_problema = []
        
        for campanha in campanhas:
            vendidos = campanha.titulos_vendidos or 0
            total = campanha.total_titulos or 0
            disponiveis = total - vendidos
            
            print(f"📊 Campanha: {campanha.titulo}")
            print(f"   ID: {campanha.id}")
            print(f"   Total configurado: {total:,}")
            print(f"   Títulos vendidos: {vendidos:,}")
            print(f"   Disponíveis: {disponiveis:,}")
            
            if disponiveis < 0:
                print(f"   ⚠️  PROBLEMA: Vendeu {abs(disponiveis):,} títulos além do limite!")
                campanhas_com_problema.append(campanha)
            else:
                print(f"   ✅ OK!")
            
            print()
        
        if not campanhas_com_problema:
            print("✅ Todas as campanhas estão OK!")
            return
        
        print("="*60)
        print("\n💡 SUGESTÕES DE CORREÇÃO:\n")
        
        for campanha in campanhas_com_problema:
            vendidos = campanha.titulos_vendidos or 0
            
            # Sugerir arredondar para próximo milhar
            if vendidos <= 10000:
                novo_limite = 10000
            elif vendidos <= 50000:
                novo_limite = 50000
            elif vendidos <= 100000:
                novo_limite = 100000
            else:
                # Arredondar para cima em blocos de 10k
                novo_limite = ((vendidos // 10000) + 1) * 10000
            
            print(f"   Campanha: {campanha.titulo}")
            print(f"   - Vendidos: {vendidos:,}")
            print(f"   - Limite atual: {campanha.total_titulos:,}")
            print(f"   - ★ Novo limite sugerido: {novo_limite:,}")
            print(f"   - Ficará disponível: {novo_limite - vendidos:,}")
            print()
        
        # Perguntar se quer aplicar
        print("="*60)
        resposta = input("\nDeseja aplicar os novos limites? (s/n): ").strip().lower()
        
        if resposta == 's':
            for campanha in campanhas_com_problema:
                vendidos = campanha.titulos_vendidos or 0
                
                if vendidos <= 10000:
                    campanha.total_titulos = 10000
                elif vendidos <= 50000:
                    campanha.total_titulos = 50000
                elif vendidos <= 100000:
                    campanha.total_titulos = 100000
                else:
                    campanha.total_titulos = ((vendidos // 10000) + 1) * 10000
                
                print(f"✅ {campanha.titulo}: limite ajustado para {campanha.total_titulos:,}")
            
            db.session.commit()
            print("\n✅ Limites ajustados com sucesso!")
            print("\n💡 Teste novamente no Postman!")
        else:
            print("\n❌ Operação cancelada.")
        
        print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    ajustar_limite_campanha()
