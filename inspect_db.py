
import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'instance', 'rifas.db')
print(f"Connecting to: {db_path}")

def get_table_info(table_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"Schema for {table_name}:")
        if not columns:
            print("Table not found or empty schema")
        for col in columns:
            # cid, name, type, notnull, dflt_value, pk
            print(col)
        conn.close()
    except Exception as e:
        print(f"Error accessing {table_name}: {e}")

get_table_info('compras')
print("-" * 20)
get_table_info('campanhas')
