"""
Script de migração: Adiciona campo expira_em na tabela compras
Execute: python add_expiracao_compras.py
"""

from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    try:
        # Para SQLite - adicionar coluna
        print("Tentando adicionar coluna 'expira_em'...")
        db.session.execute(db.text("""
            ALTER TABLE compras 
            ADD COLUMN expira_em DATETIME;
        """))
        db.session.commit()
        print("✅ Campo 'expira_em' adicionado com sucesso!")
        
        # Atualizar compras pendentes existentes (dar 10 minutos a partir de agora)
        from datetime import datetime, timedelta
        expiracao = datetime.utcnow() + timedelta(minutes=10)
        
        result = db.session.execute(db.text("""
            UPDATE compras 
            SET expira_em = :expiracao 
            WHERE status_pagamento = 'pendente' AND expira_em IS NULL;
        """), {'expiracao': expiracao})
        
        db.session.commit()
        print(f"✅ {result.rowcount} compra(s) pendente(s) atualizada(s) com prazo de expiração")
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e).lower()
        
        if 'duplicate column' in error_msg or 'already exists' in error_msg:
            print("⚠️  Campo 'expira_em' já existe na tabela 'compras'")
            print("Migração não necessária.")
        else:
            print(f"❌ Erro durante migração: {str(e)}")
            print("\nSe a coluna já existe, ignore este erro.")
            print("Se o erro persistir, execute manualmente no banco:")
            print("   ALTER TABLE compras ADD COLUMN expira_em DATETIME;")

