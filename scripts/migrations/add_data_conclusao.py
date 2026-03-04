"""
Migration: Adicionar campo data_conclusao à tabela campanhas
"""
import sys
import os

# Add project root to Python path (2 levels up)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import sqlite3

# Caminho do banco de dados
db_path = os.path.join(project_root, 'instance', 'rifas.db')

if not os.path.exists(db_path):
    print(f"❌ Banco de dados não encontrado em: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar se coluna já existe
    cursor.execute("PRAGMA table_info(campanhas)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'data_conclusao' in columns:
        print("✅ Campo 'data_conclusao' já existe!")
    else:
        print("➕ Adicionando coluna 'data_conclusao' à tabela 'campanhas'...")
        cursor.execute("ALTER TABLE campanhas ADD COLUMN data_conclusao DATE")
        conn.commit()
        print("✅ Coluna adicionada com sucesso!")
    
    # Preencher data_conclusao para campanhas já concluídas (usar data de atualização se disponível)
    cursor.execute("""
        UPDATE campanhas 
        SET data_conclusao = DATE(atualizado_em) 
        WHERE status = 'concluido' AND data_conclusao IS NULL AND atualizado_em IS NOT NULL
    """)
    rows_updated = cursor.rowcount
    conn.commit()
    
    if rows_updated > 0:
        print(f"✅ {rows_updated} campanha(s) concluída(s) atualizada(s) com data_conclusao")
    else:
        print("ℹ️  Nenhuma campanha concluída para atualizar")
    
    print("\n🎉 Migração concluída com sucesso!")

except Exception as e:
    conn.rollback()
    print(f"❌ Erro: {e}")
finally:
    conn.close()
