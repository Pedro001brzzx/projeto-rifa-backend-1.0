"""
Script para corrigir campo expira_em em compras pendentes antigas

Este script:
1. Marca compras pendentes ANTIGAS (criadas há mais de 10 min) como EXPIRADAS
2. Define expira_em = criado_em + 10 minutos para registros históricos

Execute: python scripts/fix_expired_purchases.py
"""

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.models import db, Compra
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    try:
        print("🔍 Buscando compras pendentes antigas...")
        
        # Buscar todas as compras pendentes
        compras_pendentes = Compra.query.filter_by(
            status_pagamento='pendente'
        ).all()
        
        print(f"📊 Encontradas {len(compras_pendentes)} compra(s) pendente(s)")
        
        now = datetime.utcnow()
        compras_expiradas = 0
        compras_corrigidas = 0
        
        for compra in compras_pendentes:
            # Calcular quando a compra deveria expirar (criado_em + 10 minutos)
            expiracao_correta = compra.criado_em + timedelta(minutes=10)
            
            # Se já passou de 10 minutos desde a criação, marcar como expirada
            if expiracao_correta < now:
                print(f"⏰ Compra #{compra.id} criada em {compra.criado_em} - EXPIRANDO")
                compra.status_pagamento = 'expirado'
                compra.expira_em = expiracao_correta
                compras_expiradas += 1
            else:
                # Ainda está dentro do prazo, corrigir expira_em
                if compra.expira_em != expiracao_correta:
                    print(f"✏️  Compra #{compra.id} - Corrigindo expira_em")
                    print(f"   Antigo: {compra.expira_em}")
                    print(f"   Novo:   {expiracao_correta}")
                    compra.expira_em = expiracao_correta
                    compras_corrigidas += 1
        
        # Commit das alterações
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ CORREÇÃO CONCLUÍDA!")
        print(f"   - {compras_expiradas} compra(s) marcada(s) como EXPIRADA")
        print(f"   - {compras_corrigidas} compra(s) com expira_em CORRIGIDO")
        print("="*60)
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro durante correção: {str(e)}")
        raise
