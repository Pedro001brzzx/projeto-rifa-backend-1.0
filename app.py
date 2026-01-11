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
    # Criar tabelas do banco de dados apenas na primeira execução
    # Não executar no processo de recarregamento do Flask
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        with app.app_context():
            db.create_all()
            print('✅ Tabelas do banco de dados criadas com sucesso!')
            print(f'📊 Usando banco de dados: {app.config["SQLALCHEMY_DATABASE_URI"][:20]}...')
    
    # Executar aplicação
    print('🚀 Servidor iniciado em http://127.0.0.1:5000')
    app.run(debug=True)
