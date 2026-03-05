"""
Script para atualizar a senha do admin no Railway com hash bcrypt compatível.
"""
import psycopg2
import bcrypt

DB_HOST = "maglev.proxy.rlwy.net"
DB_PORT = "28221"
DB_USER = "postgres"
DB_PASS = "JuDOhNTutfjDKNUSLTETqnUfFDSOYwZV"
DB_NAME = "railway"

try:
    print(f"Conectando ao banco de dados em {DB_HOST}:{DB_PORT}...")
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME)
    conn.autocommit = True
    cursor = conn.cursor()
    print("✅ Conexão estabelecida!")

    # Gerar hash bcrypt (compatível com flask_bcrypt)
    senha = "admin123".encode('utf-8')
    hash_bcrypt = bcrypt.hashpw(senha, bcrypt.gensalt(rounds=12)).decode('utf-8')
    print(f"🔑 Hash bcrypt gerado: {hash_bcrypt[:30]}...")

    # Atualizar o hash no banco
    cursor.execute(
        "UPDATE usuarios SET senha_hash = %s WHERE telefone = '83994099696';",
        (hash_bcrypt,)
    )
    print("✅ Senha do admin atualizada com hash bcrypt!")

    # Confirmar que o usuario existe
    cursor.execute("SELECT id, nome, telefone, is_admin, ativo FROM usuarios WHERE telefone = '83994099696';")
    row = cursor.fetchone()
    if row:
        print(f"✅ Admin confirmado: ID={row[0]}, nome={row[1]}, telefone={row[2]}, is_admin={row[3]}, ativo={row[4]}")
    else:
        print("❌ Usuário não encontrado! Verifique o banco.")

except Exception as e:
    print(f"❌ Erro: {e}")
finally:
    if 'cursor' in locals(): cursor.close()
    if 'conn' in locals(): conn.close()
    print("🔒 Conexão fechada.")
