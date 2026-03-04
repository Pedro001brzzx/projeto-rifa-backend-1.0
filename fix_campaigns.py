"""Fix existing campaigns with 'ativa' status to 'ativo'"""
import uuid
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import db, Campanha

app = create_app('default')

with app.app_context():
    fixed = 0
    for c in Campanha.query.all():
        print(f"  id={c.id} status=[{c.status}] public_id=[{c.public_id}]")
        if c.status == 'ativa':
            c.status = 'ativo'
            fixed += 1
            print(f"    -> Fixed status to 'ativo'")
        if not c.public_id:
            c.public_id = str(uuid.uuid4())
            fixed += 1
            print(f"    -> Generated public_id: {c.public_id}")
    
    if fixed > 0:
        db.session.commit()
        print(f"\n✅ Fixed {fixed} issues in existing campaigns")
    else:
        print("\n✨ All campaigns are already correct")
