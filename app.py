"""
Ponto de entrada da aplicação Flask - Gêmeos Brasil
Backend para Sistema de Campanhas/Sorteios
"""

import os
from app import create_app
from app.models import db

# Criar aplicação — usa FLASK_ENV para selecionar config (default: production no Railway)
config_name = os.getenv('FLASK_ENV', 'production')
app = create_app(config_name)

# Garantir que as tabelas existam ao iniciar
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'

    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        with app.app_context():
            db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
            # Ocultar credenciais no log
            safe_uri = db_uri.split('@')[-1] if '@' in db_uri else db_uri
            print(f'📊 Banco: ...@{safe_uri}')
        print(f'🚀 Servidor iniciado em http://0.0.0.0:{port}')

    app.run(debug=debug, host='0.0.0.0', port=port)
