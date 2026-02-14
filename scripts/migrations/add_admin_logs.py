
import sys
import os
from sqlalchemy import text

# Add root folder to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app, db
from app.models import AdminLog

app = create_app('default')

def create_admin_logs_table():
    with app.app_context():
        print("🚀 Creating admin_logs table...")
        
        # Using SQLAlchemy to create the table based on the model
        try:
            # Check if table exists
            inspector = db.inspect(db.engine)
            if 'admin_logs' not in inspector.get_table_names():
                AdminLog.__table__.create(db.engine)
                print("✅ Table admin_logs created successfully.")
            else:
                print("ℹ️  Table admin_logs already exists.")
        except Exception as e:
            print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_admin_logs_table()
