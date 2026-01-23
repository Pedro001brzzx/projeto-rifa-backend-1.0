"""
Script para executar limpeza manual de compras expiradas
"""
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
