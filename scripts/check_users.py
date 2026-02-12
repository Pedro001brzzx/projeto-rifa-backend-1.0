import sqlite3
import os

DB_PATH = os.path.join('instance', 'rifas.db')

def check_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, cpf, telefone FROM usuarios")
    users = cursor.fetchall()
    print("--- USUÁRIOS NO BANCO ---")
    for u in users:
        print(f"ID: {u[0]} | Nome: {u[1]} | Email: {u[2]} | CPF: {u[3]} | Tel: {u[4]}")
    conn.close()

if __name__ == "__main__":
    check_users()
