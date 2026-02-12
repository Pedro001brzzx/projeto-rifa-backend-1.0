import sqlite3
import os

# Caminho do banco de dados (ajuste se necessário)
DB_PATH = os.path.join('instance', 'rifas.db')

def repair_user_data():
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado em: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔍 Procurando usuários com dados incompletos...")
    
    # 1. Corrigir Emails Nulos ou Vazios
    cursor.execute("SELECT id, nome, telefone FROM usuarios WHERE email IS NULL OR email = ''")
    users_to_fix = cursor.fetchall()

    if not users_to_fix:
        print("✅ Nenhum usuário com e-mail nulo encontrado.")
    else:
        print(f"Found {len(users_to_fix)} users to fix.")
        for user_id, nome, telefone in users_to_fix:
            # Gerar um email temporário baseado no ID ou Nome se necessário
            temp_email = f"user_{user_id}@exemplo.com"
            print(f"🔧 Atualizando Usuário #{user_id} ({nome}): e-mail -> {temp_email}")
            cursor.execute("UPDATE usuarios SET email = ? WHERE id = ?", (temp_email, user_id))

    # 2. Corrigir CPFs Nulos (se houver)
    cursor.execute("SELECT id, nome FROM usuarios WHERE cpf IS NULL OR cpf = ''")
    cpfs_to_fix = cursor.fetchall()
    for user_id, nome in cpfs_to_fix:
        temp_cpf = f"{user_id:011d}" # CPF mock com 11 dígitos
        print(f"🔧 Atualizando Usuário #{user_id} ({nome}): CPF -> {temp_cpf}")
        cursor.execute("UPDATE usuarios SET cpf = ? WHERE id = ?", (temp_cpf, user_id))

    conn.commit()
    conn.close()
    print("\n✅ Reparo concluído com sucesso!")

if __name__ == "__main__":
    repair_user_data()
