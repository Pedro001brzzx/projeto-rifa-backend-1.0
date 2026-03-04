"""
Script executado no início do container no Railway.
Cria as tabelas do banco de dados e insere o primeiro usuário administrador.
"""
import os
import sys
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Adiciona a raiz do projeto ao sys.path para importações
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, Usuario
from werkzeug.security import generate_password_hash

def init_db():
    config_name = os.getenv('FLASK_ENV', 'production')
    app = create_app(config_name)
    
    with app.app_context():
        logger.info("Verificando/Criando tabelas do banco de dados...")
        try:
            db.create_all()
            logger.info("✅ Tabelas criadas com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            sys.exit(1)

        # Informações do Admin inicial
        admin_telefone = os.getenv("ADMIN_PHONE", "83994099696")
        admin_senha = os.getenv("ADMIN_PASSWORD", "admin123")
        admin_nome = "Administrador"

        # Tentar buscar o admin
        admin = Usuario.query.filter_by(telefone=admin_telefone).first()
        if admin:
            logger.info(f"O administrador {admin_telefone} já existe. Atualizando senha e previlégios...")
            admin.senha_hash = generate_password_hash(admin_senha)
            admin.is_admin = True
            db.session.commit()
            logger.info("✅ Administrador atualizado com sucesso!")
        else:
            logger.info(f"Criando novo administrador {admin_telefone}...")
            novo_admin = Usuario(
                nome=admin_nome,
                telefone=admin_telefone,
                senha_hash=generate_password_hash(admin_senha),
                is_admin=True
            )
            db.session.add(novo_admin)
            db.session.commit()
            logger.info("✅ Administrador criado com sucesso!")

if __name__ == "__main__":
    logger.info("🚀 Iniciando script de setup do Banco de Dados...")
    init_db()
