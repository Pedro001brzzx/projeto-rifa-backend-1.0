
import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'instance', 'rifas.db')

def get_table_info(table_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"Schema for {table_name}:")
        found_ativo = False
        for col in columns:
            print(col)
            if col[1] == 'ativo':
                found_ativo = True
        
        if not found_ativo:
            print(f"Column 'ativo' NOT FOUND in {table_name}")
        else:
            print(f"Column 'ativo' FOUND in {table_name}")
            
        conn.close()
    except Exception as e:
        print(f"Error accessing {table_name}: {e}")

get_table_info('usuarios')
