import sys
import os
sys.path.append(os.getcwd())

from app import app, db
from app.models.usuario import Usuario

with app.app_context():
    # Encontrar o usuário Pedro ou ID 1
    # O user log mostrava ID 1 e email pedro@exemplo.com
    usuario = Usuario.query.filter_by(id=1).first()
    
    if not usuario:
        usuario = Usuario.query.filter_by(email='pedro@exemplo.com').first()
        
    if usuario:
        old_cpf = usuario.cpf
        old_tel = usuario.telefone
        
        # Atualizar para os dados reais
        usuario.cpf = '71081729414'
        usuario.telefone = '5583994099696' # Garantindo com prefixo 55 se necessario, se ja estiver ok mantem
        
        try:
            db.session.commit()
            print(f"✅ Usuário {usuario.nome} atualizado!")
            print(f"   CPF: {old_cpf} -> {usuario.cpf}")
            print(f"   Tel: {old_tel} -> {usuario.telefone}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao atualizar: {e}")
    else:
        print("❌ Usuário não encontrado (ID 1 ou pedro@exemplo.com)")
