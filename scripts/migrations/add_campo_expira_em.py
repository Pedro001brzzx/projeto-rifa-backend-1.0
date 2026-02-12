"""
Script simplificado para adicionar campo expira_em
"""
import sys
import os

# Add project root to Python path (2 levels up)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import sqlite3
from datetime import datetime, timedelta
import os

# Caminho do banco de dados
db_path = os.path.join('instance', 'gemeos_brasil.db')

if not os.path.exists(db_path):
    print(f"❌ Banco de dados não encontrado em: {db_path}")
    print("Verifique se o caminho está correto.")
    exit(1)

# Conectar ao banco
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar se coluna já existe
    cursor.execute("PRAGMA table_info(compras)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'expira_em' in columns:
        print("✅ Campo 'expira_em' já existe!")
    else:
        # Adicionar coluna
        print("➕ Adicionando coluna 'expira_em' à tabela 'compras'...")
        cursor.execute("ALTER TABLE compras ADD COLUMN expira_em DATETIME")
        conn.commit()
        print("✅ Coluna adicionada com sucesso!")
    
    # Atualizar compras pendentes
    expiracao = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    cursor.execute("""
        UPDATE compras 
        SET expira_em = ? 
        WHERE status_pagamento = 'pendente' AND expira_em IS NULL
    """, (expiracao,))
    
    rows_updated = cursor.rowcount
    conn.commit()
    
    if rows_updated > 0:
        print(f"✅ {rows_updated} compra(s) pendente(s) atualizada(s)")
    else:
        print("ℹ️  Nenhuma compra pendente para atualizar")
    
    print("\n🎉 Migração concluída com sucesso!")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Erro: {e}")
finally:
    conn.close()
