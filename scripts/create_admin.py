"""
Cria ou atualiza o usuário administrador inicial.
Extraído de init_db.py para uso separado no Procfile do Railway.

Execute a partir da raiz do projeto:
    python scripts/create_admin.py
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario


def create_admin():
    config_name = os.getenv('FLASK_ENV', 'production')
    app = create_app(config_name)

    with app.app_context():
        admin_telefone = os.getenv('ADMIN_PHONE', '83994099696')
        admin_senha = os.getenv('ADMIN_PASSWORD', 'admin123')

        admin = Usuario.query.filter_by(telefone=admin_telefone).first()
        if admin:
            admin.set_password(admin_senha)
            admin.is_admin = True
            db.session.commit()
            logger.info(f'✅ Admin {admin_telefone} atualizado.')
        else:
            novo_admin = Usuario(
                nome='Administrador',
                telefone=admin_telefone,
                email='admin@email.com',
                cpf='00000000000',
                is_admin=True,
                ativo=True,
            )
            novo_admin.set_password(admin_senha)
            db.session.add(novo_admin)
            db.session.commit()
            logger.info(f'✅ Admin {admin_telefone} criado.')


if __name__ == '__main__':
    create_admin()
