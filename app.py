"""
Ponto de entrada da aplicação Flask - Gêmeos Brasil
Backend para Sistema de Campanhas/Sorteios
"""

import os
import sys
from app import create_app
from app.models import db

# Criar aplicação
config_name = os.getenv('FLASK_ENV', 'default')
app = create_app(config_name)


if __name__ == '__main__':
    # Criar tabelas do banco de dados em AMBOS os processos (principal e reload)
    with app.app_context():
        db.create_all()
        
    # Mostrar info apenas no processo principal
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        with app.app_context():
            print('✅ Tabelas verificadas/criadas')
            db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
            print(f'📊 Conectado ao banco: {db_uri}')
    
    # Executar aplicação
    print('🚀 Servidor iniciado em http://127.0.0.1:5000')
    app.run(debug=True)
