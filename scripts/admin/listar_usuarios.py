"""
Listar todos os usuários no banco de dados
"""
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
import sqlite3

conn = sqlite3.connect('instance/rifas.db')
cursor = conn.cursor()

cursor.execute("SELECT id, nome, telefone, email, is_admin FROM usuarios")
users = cursor.fetchall()

print("\n" + "="*80)
print("👥 TODOS OS USUÁRIOS NO BANCO DE DADOS")
print("="*80)

if not users:
    print("❌ Nenhum usuário encontrado!\n")
else:
    print(f"\n{'ID':<5} | {'Nome':<30} | {'Telefone':<15} | {'Email':<25} | {'Admin'}")
    print("-" * 80)
    
    for user in users:
        user_id, nome, telefone, email, is_admin = user
        admin_str = "✅ SIM" if is_admin else "❌ NÃO"
        email_str = email if email else "(sem email)"
        print(f"{user_id:<5} | {nome[:30]:<30} | {telefone:<15} | {email_str:<25} | {admin_str}")

print("\n" + "="*80 + "\n")

conn.close()
