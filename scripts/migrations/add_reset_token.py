
import sys
import os
from sqlalchemy import text

# Add root folder to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app, db

app = create_app('default')

def add_column_if_not_exists(conn, table, column, type_def):
    """Adds a column to a table if it doesn't exist using raw SQL"""
    try:
        # Check if column exists
        result = conn.execute(text(f"PRAGMA table_info({table})"))
        columns = [row[1] for row in result] # name is at index 1
        
        if column not in columns:
            print(f"➕ Adding column {column} to table {table}...")
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}"))
        else:
            print(f"ℹ️  Column {column} already exists in {table}.")
    except Exception as e:
        print(f"❌ Error altering table {table}: {e}")

def add_reset_token_columns():
    """Adds reset_token columns to usuarios table"""
    with app.app_context():
        print("🚀 Adding Password Recovery columns...")
        
        with db.engine.connect() as conn:
            # Add columns
            add_column_if_not_exists(conn, 'usuarios', 'reset_token', 'VARCHAR(100)')
            add_column_if_not_exists(conn, 'usuarios', 'reset_token_expiration', 'DATETIME')
            
            conn.commit()
            print("✅ Password Recovery columns added successfully.")

if __name__ == "__main__":
    add_reset_token_columns()
