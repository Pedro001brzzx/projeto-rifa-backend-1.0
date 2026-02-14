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


def forgot_password(data):
    """
    Inicia processo de recuperação de senha (Gera token e envia email)
    """
    email = data.get('email')
    
    if not email:
        return {'erro': 'E-mail é obrigatório'}, 400
    
    usuario = Usuario.query.filter_by(email=email).first()
    
    if usuario:
        token = usuario.generate_reset_token()
        db.session.commit()
        
        # MOCK EMAIL SERVICE (Log de Console)
        print(f"📧 [EMAIL MOCK] Recuperação de Senha para {email}")
        print(f"🔗 Link: https://seusite.com/reset-password?token={token}")
        print(f"🔑 Token: {token}")
        
    # Segurança: Nunca revelar se o email existe ou não
    return {
        'mensagem': 'Se o e-mail estiver cadastrado, você receberá um link com instruções.'
    }, 200


def reset_password(data):
    """
    Redefine a senha usando o token de recuperação
    """
    token = data.get('token')
    nova_senha = data.get('senha')
    
    if not token or not nova_senha:
        return {'erro': 'Token e nova senha são obrigatórios'}, 400
        
    # Validar complexidade da senha (mínimo 6 caracteres por enquanto)
    if len(nova_senha) < 6:
        return {'erro': 'A senha deve ter no mínimo 6 caracteres'}, 400
        
    usuario = Usuario.query.filter_by(reset_token=token).first()
    
    if not usuario or not usuario.is_reset_token_valid(token):
        return {'erro': 'Token inválido ou expirado'}, 400
        
    # Redefinir senha
    usuario.set_password(nova_senha)
    
    # Invalidar token
    usuario.reset_token = None
    usuario.reset_token_expiration = None
    
    db.session.commit()
    
    return {'mensagem': 'Senha redefinida com sucesso! Faço login com sua nova senha.'}, 200


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
