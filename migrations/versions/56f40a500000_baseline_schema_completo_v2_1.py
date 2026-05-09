"""baseline: schema completo v2.1

Revision ID: 56f40a500000
Revises:
Create Date: 2026-05-09 01:02:31.796394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56f40a500000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Baseline: schema v2.1 já criado via db.create_all() em wsgi.py/app.py.
    # Esta migration serve como marcador de versão inicial do schema.
    # Mudanças futuras de schema serão geradas aqui como ALTER TABLE normais.
    pass


def downgrade():
    pass
