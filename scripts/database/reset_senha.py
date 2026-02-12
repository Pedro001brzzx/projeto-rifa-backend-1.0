"""
Script para redefinir senha de usuários em ambiente de desenvolvimento
Execute: python reset_senha.py
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

def resetar_senha():
    with app.app_context():
        print("="*50)
        print("🔑 GERENCIADOR DE SENHAS (DEV)")
        print("="*50)
        
        # Listar usuários
        usuarios = Usuario.query.all()
        
        if not usuarios:
            print("❌ Nenhum usuário encontrado no banco de dados.")
            return

        print(f"\nEncontrados {len(usuarios)} usuários:\n")
        print(f"{'ID':<5} | {'Nome':<30} | {'Telefone':<15} | {'Admin'}")
        print("-" * 65)
        
        for u in usuarios:
            admin_status = "✅ SIM" if u.is_admin else "❌ NÃO"
            print(f"{u.id:<5} | {u.nome[:30]:<30} | {u.telefone:<15} | {admin_status}")
            
        print("\n" + "="*50)
        
        # Solicitar ID
        try:
            user_id = input("\nDigite o ID do usuário para mudar a senha (ou Enter para sair): ")
            usuario = db.session.get(Usuario, int(user_id))
            
            if not usuario:
                print("❌ Usuário não encontrado!")
                return
                
            nova_senha = input(f"Digite a nova senha para '{usuario.nome}': ")
            if not nova_senha: return
            
            # Atualizar senha
            usuario.set_senha(nova_senha)
            db.session.commit()
            
            print(f"\n✅ SUCESSO! Senha de '{usuario.nome}' alterada para '{nova_senha}'")
            print("Agora você pode fazer login com esta nova senha.")
            
        except ValueError:
            print("❌ ID inválido.")
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == '__main__':
    resetar_senha()
