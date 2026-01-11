"""
Script para tornar um usuário administrador
Execute: python make_admin.py
"""

from app import create_app
from app.models import db, Usuario

def make_admin():
    app = create_app()
    
    with app.app_context():
        # Solicita o telefone do usuário
        telefone = input('Digite o telefone do usuário (ex: 11999999999): ').strip()
        
        # Busca o usuário
        usuario = Usuario.query.filter_by(telefone=telefone).first()
        
        if not usuario:
            print(f'❌ Usuário com telefone {telefone} não encontrado!')
            print('\nUsuários cadastrados:')
            todos_usuarios = Usuario.query.all()
            for u in todos_usuarios:
                admin_status = '👑 Admin' if u.is_admin else '👤 Usuário'
                print(f'  - {u.nome} ({u.telefone}) - {admin_status}')
            return
        
        # Verifica se já é admin
        if usuario.is_admin:
            print(f'ℹ️  {usuario.nome} já é administrador!')
            return
        
        # Torna admin
        usuario.is_admin = True
        db.session.commit()
        
        print(f'✅ {usuario.nome} agora é administrador!')
        print(f'📧 Email: {usuario.email}')
        print(f'📞 Telefone: {usuario.telefone}')
        print(f'\nVocê pode fazer login e criar campanhas!')

if __name__ == '__main__':
    make_admin()
