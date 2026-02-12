"""
Script para verificar e corrigir senha do usuário
"""
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Conectar ao banco
conn = sqlite3.connect('instance/rifas.db')
cursor = conn.cursor()

# Buscar o usuário com telefone 83994099696
cursor.execute("SELECT id, nome, telefone, senha_hash FROM usuarios WHERE telefone = ?", ('83994099696',))
user = cursor.fetchone()

if user:
    user_id, nome, telefone, senha_hash_atual = user
    print("="*60)
    print("🔍 USUÁRIO ENCONTRADO")
    print("="*60)
    print(f"ID: {user_id}")
    print(f"Nome: {nome}")
    print(f"Telefone: {telefone}")
    print(f"\nHash atual: {senha_hash_atual[:50]}...")
    
    # Testar senhas comuns
    senhas_teste = ['12345', '123456', 'admin', '1234']
    print("\n🔑 Testando senhas comuns:")
    for senha in senhas_teste:
        if check_password_hash(senha_hash_atual, senha):
            print(f"✅ SENHA CORRETA: '{senha}'")
            conn.close()
            exit()
        else:
            print(f"❌ Não é '{senha}'")
    
    print("\n" + "="*60)
    print("⚠️  Nenhuma senha comum funcionou.")
    print("Criando nova senha...")
    
    # Resetar para senha padrão
    nova_senha = '123456'
    novo_hash = generate_password_hash(nova_senha)
    
    cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", (novo_hash, user_id))
    conn.commit()
    
    print(f"\n✅ SENHA RESETADA COM SUCESSO!")
    print(f"Nova senha: {nova_senha}")
    print(f"Telefone: {telefone}")
    print("\nAgora você pode fazer login com:")
    print(f"  Telefone: {telefone}")
    print(f"  Senha: {nova_senha}")
else:
    print("❌ Usuário com telefone 83994099696 não encontrado!")

conn.close()
