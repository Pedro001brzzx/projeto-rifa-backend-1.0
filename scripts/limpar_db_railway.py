"""
Script para limpar tabelas corrompidas do PostgreSQL via Connection String remota.
"""
import psycopg2
from urllib.parse import urlparse

DB_URL = "postgresql://postgres:JuDOhNTutfjDKNUSLTETqnUfFDSOYwZV@postgres.railway.internal:5432/railway"

# Como a connection string usa '.internal', preciso trocar para acesso externo caso exista
# Mas como estamos no local, vamos só imprimir a query para o usuário rodar no painel
print("Para limpar a tabela `usuarios` com erro no Railway, execute no painel SQL:")
print("DROP TABLE IF EXISTS usuarios CASCADE;")
print("DROP TABLE IF EXISTS alembic_version CASCADE;")
