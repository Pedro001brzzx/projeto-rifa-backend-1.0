"""
Script simples para resetar senha diretamente no banco de dados
"""
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
import sqlite3
from werkzeug.security import generate_password_hash

# Conectar ao banco
conn = sqlite3.connect('instance/rifas.db')
cursor = conn.cursor()

# Verificar usuário existente
cursor.execute("SELECT id, nome, telefone FROM usuarios")
users = cursor.fetchall()

print("\n" + "="*50)
print("👥 USUÁRIOS NO BANCO")
print("="*50)

if not users:
    print("❌ Nenhum usuário encontrado!")
    conn.close()
    exit()

for user in users:
    print(f"ID: {user[0]} | Nome: {user[1]} | Telefone: {user[2]}")

print("\n" + "="*50)

# Solicitar dados
user_id = input("\nDigite o ID do usuário para resetar a senha: ")
nova_senha = input("Digite a nova senha: ")

if not user_id or not nova_senha:
    print("❌ Operação cancelada.")
    conn.close()
    exit()

# Gerar hash da senha
senha_hash = generate_password_hash(nova_senha)

# Atualizar senha
cursor.execute(
    "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
    (senha_hash, int(user_id))
)
conn.commit()

# Confirmar
cursor.execute("SELECT nome, telefone FROM usuarios WHERE id = ?", (int(user_id),))
user = cursor.fetchone()

print(f"\n✅ SUCESSO!")
print(f"Senha de '{user[0]}' (telefone: {user[1]}) foi alterada para: {nova_senha}")
print("\nAgora você pode fazer login com esta senha.")

conn.close()
