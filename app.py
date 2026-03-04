"""
Ponto de entrada da aplicação Flask - Gêmeos Brasil
Backend para Sistema de Campanhas/Sorteios
"""

import os
import sys
import logging
from app import create_app
from app.models import db

# Configurar logging básico para ver erros no Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Criar aplicação
config_name = os.getenv('FLASK_ENV', 'production')
logger.info(f"🔧 Iniciando app com config: {config_name}")

try:
    app = create_app(config_name)
    logger.info("✅ App Flask criado com sucesso")
except Exception as e:
    logger.error(f"❌ Falha ao criar app Flask: {e}")
    raise

# Criar tabelas do banco de dados
try:
    with app.app_context():
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        safe_uri = ("..." + db_uri.split('@')[-1]) if '@' in db_uri else db_uri
        logger.info(f"📊 Conectando ao banco: {safe_uri}")
        db.create_all()
        logger.info("✅ Tabelas verificadas/criadas com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao criar tabelas: {e}")
    logger.error("⚠️  Verifique se DATABASE_URL está configurada nas variáveis de ambiente")
    raise

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = config_name == 'development'
    logger.info(f"🚀 Servidor iniciado em http://0.0.0.0:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
