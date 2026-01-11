from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    usuario = Usuario.query.filter_by(
        telefone=data.get('telefone')
    ).first()

    if not usuario or not usuario.verificar_senha(data.get('senha')):
        return jsonify({'erro': 'Credenciais inválidas'}), 401

    token = create_access_token(identity=usuario.id)

    return jsonify({
        'token': token,
        'usuario': usuario.to_dict()
    })
