"""
Script para executar cleanup de compras expiradas
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.jobs.cleanup_expired_purchases import cancelar_compras_expiradas

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("   LIMPEZA DE COMPRAS EXPIRADAS")
    print("="*60 + "\n")
    
    result = cancelar_compras_expiradas()
    
    print(f"\n✅ Total de compras canceladas: {result}")
    print("\n" + "="*60 + "\n")
