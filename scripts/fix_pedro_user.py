import sqlite3
import os

DB_PATH = os.path.join('instance', 'rifas.db')

def fix_specific_user():
    if not os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET email = 'pedro@exemplo.com' WHERE cpf = '00011122233'")
    print(f"✅ Usuário com CPF 00011122233 atualizado! Linhas afetadas: {cursor.rowcount}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_specific_user()
