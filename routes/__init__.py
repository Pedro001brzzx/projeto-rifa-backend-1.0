from .auth import auth_bp
from .campanhas import campanhas_bp
from .compras import compras_bp
from .conteudo import conteudo_bp
from .publico import publico_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(campanhas_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(conteudo_bp)
    app.register_blueprint(publico_bp)
