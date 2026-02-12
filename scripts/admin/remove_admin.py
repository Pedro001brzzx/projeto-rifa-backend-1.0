"""
Script para remover privilégios de administrador
Execute: python remove_admin.py
"""

import sys
import os

# Add parent directory to Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from app import create_app
from app.models import db, Usuario

app = create_app()

def remover_admin():
    with app.app_context():
        print("="*50)
        print("👮 REMOVEDOR DE ADMIN")
        print("="*50)
        
        # Listar admins atuais
        admins = Usuario.query.filter_by(is_admin=True).all()
        
        if not admins:
            print("❌ Nenhum administrador encontrado.")
            return

        print(f"\nAdministradores atuais:\n")
        print(f"{'ID':<5} | {'Nome':<30} | {'Telefone':<15}")
        print("-" * 55)
        
        for u in admins:
            print(f"{u.id:<5} | {u.nome[:30]:<30} | {u.telefone:<15}")
            
        print("\n" + "="*50)
        
        telefone = input("\nDigite o telefone do usuário para remover admin (ou Enter para sair): ").strip()
        
        if not telefone:
            return
            
        # Tenta buscar pelo telefone exato
        usuario = Usuario.query.filter_by(telefone=telefone).first()
        
        # Tenta com 55 se não achar
        if not usuario and len(telefone) in [10, 11]:
             usuario = Usuario.query.filter_by(telefone=f"55{telefone}").first()
        
        if not usuario:
            print("❌ Usuário não encontrado!")
            return
            
        if not usuario.is_admin:
            print(f"ℹ️  {usuario.nome} já NÃO é administrador!")
            return
            
        usuario.is_admin = False
        db.session.commit()
        
        print(f"✅ SUCESSO! Privilégios de admin removidos de {usuario.nome} ({usuario.telefone})")

if __name__ == '__main__':
    remover_admin()
