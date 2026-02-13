import sqlite3
import os

db_path = os.path.join('instance', 'rifas.db')

if not os.path.exists(db_path):
    print(f"❌ Banco de dados não encontrado: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar usuários existentes
    cursor.execute("SELECT id, nome, email, cpf, telefone FROM usuarios")
    users = cursor.fetchall()
    print("📋 Usuários encontrados:")
    for u in users:
        print(u)
        
    # Atualizar Pedro (assumindo ID 1 ou email pedro@exemplo.com)
    # Vou usar email como chave para ter certeza
    email_target = 'pedro@exemplo.com'
    new_cpf = '71081729414'
    new_phone = '5583994099696'
    
    cursor.execute("UPDATE usuarios SET cpf = ?, telefone = ? WHERE email = ?", (new_cpf, new_phone, email_target))
    
    if cursor.rowcount > 0:
        print(f"\n✅ Usuário {email_target} atualizado com sucesso!")
        conn.commit()
    else:
        print(f"\n❌ Usuário {email_target} não encontrado para atualização.")
        
        # Tentar pelo ID 1 se email falhar (caso o email no banco seja diferente)
        cursor.execute("UPDATE usuarios SET cpf = ?, telefone = ? WHERE id = 1", (new_cpf, new_phone))
        if cursor.rowcount > 0:
            print("✅ Usuário ID 1 atualizado com sucesso!")
            conn.commit()

except Exception as e:
    print(f"\n❌ Erro: {e}")
    conn.rollback()
finally:
    conn.close()
