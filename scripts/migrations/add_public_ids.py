
import uuid
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

def populate_public_ids():
    """Populates public_id for records that don't have it using raw SQL"""
    with app.app_context():
        print("🚀 Starting Public ID Migration (Raw SQL Mode)...")
        
        with db.engine.connect() as conn:
            # 1. Ensure columns exist
            add_column_if_not_exists(conn, 'campanhas', 'public_id', 'VARCHAR(36)')
            add_column_if_not_exists(conn, 'usuarios', 'public_id', 'VARCHAR(36)')
            add_column_if_not_exists(conn, 'compras', 'public_id', 'VARCHAR(36)')
            conn.commit()

            # 2. Populate UUIDs
            tables = ['campanhas', 'usuarios', 'compras']
            
            for table in tables:
                # Find records without public_id
                result = conn.execute(text(f"SELECT id FROM {table} WHERE public_id IS NULL"))
                ids_to_update = [row[0] for row in result]
                
                count = 0
                if ids_to_update:
                    print(f"🔄 Updating {len(ids_to_update)} records in {table}...")
                    for record_id in ids_to_update:
                        new_uuid = str(uuid.uuid4())
                        conn.execute(
                            text(f"UPDATE {table} SET public_id = :uuid WHERE id = :id"),
                            {"uuid": new_uuid, "id": record_id}
                        )
                        count += 1
                    conn.commit()
                    print(f"✅ Generated UUIDs for {count} {table} records.")
                else:
                    print(f"✨ No {table} records needed updates.")

if __name__ == "__main__":
    populate_public_ids()
