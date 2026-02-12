
import sqlite3
import os

# Path to database
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'rifas.db')

def update_db():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(compras)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'pix_copia_cola' not in columns:
        print("Adding pix_copia_cola column...")
        cursor.execute("ALTER TABLE compras ADD COLUMN pix_copia_cola TEXT")
    else:
        print("pix_copia_cola already exists.")
        
    if 'pix_qr_code_base64' not in columns:
        print("Adding pix_qr_code_base64 column...")
        cursor.execute("ALTER TABLE compras ADD COLUMN pix_qr_code_base64 TEXT")
    else:
        print("pix_qr_code_base64 already exists.")
        
    conn.commit()
    conn.close()
    print("Database update complete.")

if __name__ == "__main__":
    update_db()
