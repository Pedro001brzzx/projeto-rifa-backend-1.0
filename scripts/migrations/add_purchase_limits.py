"""
Migração: Adicionar campos de limites de compra (min/max quantidade)
"""
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    try:
        print("🔧 Adicionando campos de limites de compra...")
        
        # Check if columns already exist
        result = db.session.execute("PRAGMA table_info(campanhas)")
        columns = [col[1] for col in result.fetchall()]
        
        if 'min_quantidade_compra' in columns:
            print("⚠️  Coluna min_quantidade_compra já existe")
        else:
            # Add min_quantidade_compra column (SQLite compatible)
            db.session.execute("""
                ALTER TABLE campanhas 
                ADD COLUMN min_quantidade_compra INTEGER
            """)
            # Set default value for existing rows
            db.session.execute("""
                UPDATE campanhas 
                SET min_quantidade_compra = 1 
                WHERE min_quantidade_compra IS NULL
            """)
            print("✅ Coluna min_quantidade_compra adicionada")
        
        if 'max_quantidade_compra' in columns:
            print("⚠️  Coluna max_quantidade_compra já existe")
        else:
            # Add max_quantidade_compra column (nullable)
            db.session.execute("""
                ALTER TABLE campanhas 
                ADD COLUMN max_quantidade_compra INTEGER
            """)
            print("✅ Coluna max_quantidade_compra adicionada")
        
        db.session.commit()
        print("\n✅ Migração concluída com sucesso!")
        
        # Show updated schema
        print("\n📋 Verificando colunas...")
        result = db.session.execute("PRAGMA table_info(campanhas)")
        columns = result.fetchall()
        
        print("\nColunas da tabela 'campanhas':")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro na migração: {str(e)}")
        import traceback
        traceback.print_exc()
