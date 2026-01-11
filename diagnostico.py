"""
Script de Diagnóstico - Verifica status de campanhas, compras e títulos
"""

from app import create_app
from app.models import db, Campanha, Compra, Titulo

def diagnostico():
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("DIAGNÓSTICO DO SISTEMA DE TÍTULOS")
        print("=" * 60)
        
        # 1. Campanhas
        print("\n📊 CAMPANHAS:")
        campanhas = Campanha.query.all()
        if not campanhas:
            print("   ⚠️  Nenhuma campanha encontrada!")
        else:
            for c in campanhas:
                print(f"\n   ID: {c.id}")
                print(f"   Título: {c.titulo}")
                print(f"   Status: {c.status}")
                print(f"   Total títulos: {c.total_titulos}")
                print(f"   ★ Vendidos (contador): {c.titulos_vendidos}")
        
        # 2. Compras
        print("\n" + "=" * 60)
        print("💰 COMPRAS:")
        compras = Compra.query.all()
        if not compras:
            print("   ⚠️  Nenhuma compra encontrada!")
        else:
            pendentes = 0
            aprovadas = 0
            for c in compras:
                if c.status_pagamento == 'pendente':
                    pendentes += 1
                elif c.status_pagamento == 'aprovado':
                    aprovadas += 1
                    
                print(f"\n   ID: {c.id}")
                print(f"   Campanha ID: {c.campanha_id}")
                print(f"   Usuário ID: {c.usuario_id}")
                print(f"   Quantidade: {c.quantidade_titulos}")
                print(f"   ★ Status: {c.status_pagamento}")
            
            print(f"\n   📊 Resumo:")
            print(f"   - Aprovadas: {aprovadas}")
            print(f"   - Pendentes: {pendentes}")
        
        # 3. Títulos
        print("\n" + "=" * 60)
        print("🎟️  TÍTULOS:")
        titulos = Titulo.query.all()
        print(f"   Total de títulos no banco: {len(titulos)}")
        
        if titulos:
            # Agrupar por campanha
            titulos_por_campanha = {}
            for t in titulos:
                # Verificar se tem campanha_id (novo campo)
                campanha_id = getattr(t, 'campanha_id', None)
                if campanha_id is None:
                    # Buscar via compra
                    campanha_id = t.compra.campanha_id if t.compra else None
                
                if campanha_id:
                    if campanha_id not in titulos_por_campanha:
                        titulos_por_campanha[campanha_id] = 0
                    titulos_por_campanha[campanha_id] += 1
            
            print(f"\n   📊 Títulos por campanha:")
            for camp_id, qtd in titulos_por_campanha.items():
                campanha = Campanha.query.get(camp_id)
                nome = campanha.titulo if campanha else "Desconhecida"
                print(f"   - Campanha {camp_id} ({nome}): {qtd} títulos")
        
        # 4. Diagnóstico de problemas
        print("\n" + "=" * 60)
        print("🔍 DIAGNÓSTICO:")
        
        problemas = []
        
        # Verificar compras pendentes
        compras_pendentes = Compra.query.filter_by(status_pagamento='pendente').count()
        if compras_pendentes > 0:
            problemas.append(f"⚠️  {compras_pendentes} compra(s) PENDENTE(s) - Execute 'python aprovar_compras.py'")
        
        # Verificar se contador está zerado mas há títulos
        for campanha in campanhas:
            titulos_reais = Titulo.query.join(Compra).filter(
                Compra.campanha_id == campanha.id
            ).count()
            
            if campanha.titulos_vendidos == 0 and titulos_reais > 0:
                problemas.append(f"⚠️  Campanha '{campanha.titulo}' tem {titulos_reais} títulos mas contador está em 0")
            elif campanha.titulos_vendidos != titulos_reais:
                problemas.append(f"⚠️  Campanha '{campanha.titulo}': contador={campanha.titulos_vendidos}, real={titulos_reais}")
        
        # Verificar campo campanha_id em títulos
        if titulos:
            primeiro_titulo = titulos[0]
            if not hasattr(primeiro_titulo, 'campanha_id'):
                problemas.append("⚠️  Campo 'campanha_id' NÃO EXISTE na tabela titulos - Execute migration!")
        
        if problemas:
            print("\n   ❌ PROBLEMAS ENCONTRADOS:")
            for p in problemas:
                print(f"   {p}")
        else:
            print("\n   ✅ Sistema OK!")
        
        print("\n" + "=" * 60)
        
        # 5. Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        if compras_pendentes > 0:
            print("   1. Execute: python aprovar_compras.py")
        
        if any("contador" in p for p in problemas):
            print("   2. O contador está dessincronizado. Aprovar compras deve corrigir.")
        
        if any("migration" in p.lower() for p in problemas):
            print("   3. Execute a migration do banco de dados (migration.sql)")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    diagnostico()
