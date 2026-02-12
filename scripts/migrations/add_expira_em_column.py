"""
Script para adicionar o campo expira_em à tabela compras
Execute SOMENTE UMA VEZ após adicionar o campo ao modelo
"""

import sys
import os

# Add project root to Python path (2 levels up from migrations/)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    try:
        print("🔧 Adicionando coluna expira_em à tabela compras...")
        
        # Executar ALTER TABLE para adicionar a coluna
        db.session.execute(db.text("""
            ALTER TABLE compras 
            ADD COLUMN expira_em DATETIME NULL
        """))
        
        db.session.commit()
        
        print("✅ Coluna expira_em adicionada com sucesso!")
        print("📝 Próximo passo: Execute python .\\scripts\\fix_expired_purchases.py")
        
    except Exception as e:
        db.session.rollback()
        
        # Se a coluna já existe, ignorar erro
        if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
            print("ℹ️  Coluna expira_em já existe no banco de dados")
        else:
            print(f"❌ Erro ao adicionar coluna: {str(e)}")
            raise
