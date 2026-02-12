"""
Controller de Autenticação
Contém a lógica de negócio para registro, login e perfil de usuários
"""

from flask import jsonify
from flask_jwt_extended import create_access_token
from app.models import db, Usuario

from app.utils.helpers import somente_numeros

def registro_usuario(data):
    """
    Registra um novo usuário no sistema
    """
    # Sanitização e Validação
    nome = str(data.get('nome') or "").strip()
    email = str(data.get('email') or "").strip().lower()
    telefone = somente_numeros(data.get('telefone'))
    cpf = somente_numeros(data.get('cpf'))
    senha = data.get('senha')

    if not telefone or not senha or not nome or not email or not cpf:
        return {'erro': 'Nome, e-mail, telefone, CPF e senha são obrigatórios'}, 400
    
    if len(cpf) != 11:
        return {'erro': 'CPF deve conter exatamente 11 dígitos'}, 400
    
    if len(telefone) < 10:
        return {'erro': 'Telefone inválido (mínimo 10 dígitos)'}, 400

    # Verificar se usuário já existe
    if Usuario.query.filter_by(telefone=telefone).first():
        return {'erro': 'Telefone já cadastrado'}, 400
    
    if Usuario.query.filter_by(email=email).first():
        return {'erro': 'Email já cadastrado'}, 400
    
    if Usuario.query.filter_by(cpf=cpf).first():
        return {'erro': 'CPF já cadastrado'}, 400
    
    # Criar novo usuário
    usuario = Usuario(
        nome=nome,
        telefone=telefone,
        email=email,
        cpf=cpf,
        cidade=data.get('cidade'),
        estado=data.get('estado')
    )
    usuario.set_senha(senha)
    
    db.session.add(usuario)
    db.session.commit()
    
    token = create_access_token(identity=str(usuario.id))
    
    return {
        'mensagem': 'Usuário cadastrado com sucesso',
        'token': token,
        'usuario': usuario.to_dict()
    }, 201


def login_usuario(data):
    """
    Realiza login do usuário com sanitização de telefone
    """
    telefone_bruto = data.get('telefone')
    senha = data.get('senha')

    if not telefone_bruto or not senha:
        return {'erro': 'Por favor, preencha telefone e senha'}, 400
    
    telefone = somente_numeros(telefone_bruto)
        
    # Tenta buscar pelo telefone purificado
    usuario = Usuario.query.filter_by(telefone=telefone).first()
    
    # Se não encontrou, tenta adicionar o DDI 55 (Brasil) caso o número tenha 10 ou 11 dígitos
    if not usuario and telefone and len(telefone) in [10, 11]:
        usuario = Usuario.query.filter_by(telefone=f"55{telefone}").first()
    
    if not usuario or not usuario.verificar_senha(senha):
        return {'erro': 'Telefone ou senha inválidos'}, 401
    
    if not usuario.ativo:
        return {'erro': 'Usuário inativo'}, 403
    
    token = create_access_token(identity=str(usuario.id))
    
    return {
        'mensagem': 'Login realizado com sucesso',
        'token': token,
        'usuario': usuario.to_dict()
    }, 200


def recuperar_senha(data):
    """
    Inicia processo de recuperação de senha
    
    Args:
        data: Dicionário com telefone
    
    Returns:
        tuple: (response dict, status code)
    """
    if not data.get('telefone'):
        return {'erro': 'Telefone é obrigatório'}, 400
    
    usuario = Usuario.query.filter_by(telefone=data['telefone']).first()
    
    if not usuario:
        return {
            'mensagem': 'Se o telefone estiver cadastrado, você receberá um SMS com instruções'
        }, 200
    
    # TODO: Implementar envio de SMS com token de recuperação
    
    return {'mensagem': 'SMS enviado com sucesso'}, 200


def obter_perfil(usuario_id):
    """
    Obtém os dados do perfil do usuário
    
    Args:
        usuario_id: ID do usuário autenticado
    
    Returns:
        tuple: (response dict, status code)
    """
    # Converter de volta para inteiro (JWT retorna string)
    usuario = Usuario.query.get(int(usuario_id))
    
    if not usuario:
        return {'erro': 'Usuário não encontrado'}, 404
    
    return usuario.to_dict(), 200


def atualizar_perfil(usuario_id, data):
    """
    Atualiza os dados do perfil do usuário
    
    Args:
        usuario_id: ID do usuário autenticado
        data: Dicionário com dados a serem atualizados
    
    Returns:
        tuple: (response dict, status code)
    """
    # Converter de volta para inteiro (JWT retorna string)
    usuario = Usuario.query.get(int(usuario_id))
    
    if not usuario:
        return {'erro': 'Usuário não encontrado'}, 404
    
    # Atualizar campos permitidos
    if data.get('nome'):
        usuario.nome = data['nome']
    if data.get('email'):
        usuario.email = data['email']
    if data.get('endereco'):
        usuario.endereco = data['endereco']
    if data.get('cidade'):
        usuario.cidade = data['cidade']
    if data.get('estado'):
        usuario.estado = data['estado']
    if data.get('cep'):
        usuario.cep = data['cep']
    
    db.session.commit()
    
    return {
        'mensagem': 'Perfil atualizado com sucesso',
        'usuario': usuario.to_dict()
    }, 200
