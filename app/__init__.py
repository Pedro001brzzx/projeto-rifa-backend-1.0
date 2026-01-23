"""
Inicialização da Aplicação Flask - Gêmeos Brasil
Factory Pattern para criação da aplicação
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import config
from app.models import db, bcrypt


def create_app(config_name='default'):
    """
    Factory function para criar a aplicação Flask
    
    Args:
        config_name: Nome da configuração a ser usada (default, development, production)
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Carregar configurações
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    
    # Configurar CORS para aceitar requisições do frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",  # Create React App
                "http://localhost:5173",  # Vite
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Registrar blueprints
    registrar_blueprints(app)
    
    # Registrar rota principal
    registrar_rota_principal(app)
    
    # Inicializar scheduler de tarefas em background
    try:
        from app.scheduler import init_scheduler
        init_scheduler(app)
    except ImportError:
        app.logger.warning("APScheduler não instalado. Execute: pip install apscheduler")
    except Exception as e:
        app.logger.error(f"Erro ao iniciar scheduler: {str(e)}")
    
    return app


def registrar_blueprints(app):
    """
    Registra todos os blueprints da aplicação
    
    Args:
        app: Instância Flask
    """
    from app.routes import (
        auth_bp,
        campanha_bp,
        compra_bp,
        ganhador_bp,
        conteudo_bp,
        pagamento_bp,
        admin_bp
    )
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(campanha_bp)
    app.register_blueprint(compra_bp)
    app.register_blueprint(ganhador_bp)
    app.register_blueprint(conteudo_bp)
    app.register_blueprint(pagamento_bp)
    app.register_blueprint(admin_bp)


def registrar_rota_principal(app):
    """
    Registra a rota principal da API
    
    Args:
        app: Instância Flask
    """
    @app.route('/')
    def index():
        return jsonify({
            'mensagem': 'API Gêmeos Brasil',
            'versao': '1.0',
            'endpoints': {
                'auth': '/api/auth',
                'campanhas': '/api/campanhas',
                'compras': '/api/compras',
                'checkout': '/api/checkout',
                'pagamentos': '/api/pagamentos',
                'ganhadores': '/api/ganhadores',
                'artigos': '/api/artigos',
                'comunicados': '/api/comunicados',
                'contato': '/api/contato'
            }
        }), 200
