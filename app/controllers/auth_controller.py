"""
Controller de Autenticação
Contém a lógica de negócio para registro, login e perfil de usuários
"""

from flask import jsonify
from flask_jwt_extended import create_access_token
from app.models import db, Usuario


def registro_usuario(data):
    """
    Registra um novo usuário no sistema
    
    Args:
        data: Dicionário com dados do usuário (nome, telefone, senha, etc)
    
    Returns:
        tuple: (response dict, status code)
    """
    # Validação
    if not data.get('telefone') or not data.get('senha') or not data.get('nome'):
        return {'erro': 'Nome, telefone e senha são obrigatórios'}, 400
    
    # Verificar se usuário já existe
    if Usuario.query.filter_by(telefone=data['telefone']).first():
        return {'erro': 'Telefone já cadastrado'}, 400
    
    if data.get('email') and Usuario.query.filter_by(email=data['email']).first():
        return {'erro': 'Email já cadastrado'}, 400
    
    # Criar novo usuário
    usuario = Usuario(
        nome=data['nome'],
        telefone=data['telefone'],
        email=data.get('email'),
        cpf=data.get('cpf'),
        cidade=data.get('cidade'),
        estado=data.get('estado')
    )
    usuario.set_senha(data['senha'])
    
    db.session.add(usuario)
    db.session.commit()
    
    # Gerar token (JWT requer string como identity)
    token = create_access_token(identity=str(usuario.id))
    
    return {
        'mensagem': 'Usuário cadastrado com sucesso',
        'token': token,
        'usuario': usuario.to_dict()
    }, 201


def login_usuario(data):
    """
    Realiza login do usuário
    
    Args:
        data: Dicionário com telefone e senha
    
    Returns:
        tuple: (response dict, status code)
    """
    # Debug logging (apenas para desenvolvimento)
    print(f"[LOGIN DEBUG] Dados recebidos: {data}")
    print(f"[LOGIN DEBUG] Telefone: {data.get('telefone')}")
    print(f"[LOGIN DEBUG] Senha presente: {bool(data.get('senha'))}")
    
    # Validação de campos obrigatórios
    # Retorna mensagem genérica ao usuário por segurança
    if not data.get('telefone') or not data.get('senha'):
        print(f"[LOGIN DEBUG] Validação falhou - Telefone: {bool(data.get('telefone'))}, Senha: {bool(data.get('senha'))}")
        return {'erro': 'Por favor, preencha telefone e senha'}, 400
    
    telefone = data['telefone']
        
    # Tenta buscar pelo telefone exato
    usuario = Usuario.query.filter_by(telefone=telefone).first()
    
    # Se não encontrou, tenta adicionar o DDI 55 (Brasil) caso o número tenha 10 ou 11 dígitos
    # Ex: usuário digitou 83994099696, mas no banco está 5583994099696
    if not usuario and telefone.isdigit() and len(telefone) in [10, 11]:
        usuario = Usuario.query.filter_by(telefone=f"55{telefone}").first()
    
    if not usuario or not usuario.verificar_senha(data['senha']):
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
