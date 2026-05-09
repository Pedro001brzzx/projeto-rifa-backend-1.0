"""
Migração Fase B — v2.1
Adiciona coluna deleted_at (soft delete) em campanhas, compras e usuarios.

Execute a partir da raiz do projeto:
    python scripts/migrate_fase_b.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from sqlalchemy import text, inspect


def coluna_existe(conn, tabela, coluna):
    inspector = inspect(conn)
    colunas = [c['name'] for c in inspector.get_columns(tabela)]
    return coluna in colunas


def main():
    app = create_app()

    alteracoes = [
        ('campanhas', 'deleted_at', 'TIMESTAMP NULL'),
        ('compras',   'deleted_at', 'TIMESTAMP NULL'),
        ('usuarios',  'deleted_at', 'TIMESTAMP NULL'),
    ]

    with app.app_context():
        with db.engine.connect() as conn:
            for tabela, coluna, tipo in alteracoes:
                if coluna_existe(conn, tabela, coluna):
                    print(f'⏭️  {tabela}.{coluna} já existe — ignorado')
                    continue
                try:
                    conn.execute(text(f'ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}'))
                    conn.commit()
                    print(f'✅  {tabela}.{coluna} adicionado')
                except Exception as e:
                    conn.rollback()
                    print(f'❌  {tabela}.{coluna}: {e}')

    print('\nMigração Fase B concluída.')


if __name__ == '__main__':
    main()
