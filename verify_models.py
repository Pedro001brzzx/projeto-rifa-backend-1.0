
from app import create_app
from app.models import db, Compra, Campanha, Titulo, Usuario

app = create_app()

with app.app_context():
    try:
        print("Verifying models...")
        # Inspect columns
        print(f"Compra columns: {Compra.__table__.columns.keys()}")
        print(f"Campanha columns: {Campanha.__table__.columns.keys()}")
        print(f"Usuario columns: {Usuario.__table__.columns.keys()}")
        
        # Verify relationships and attributes
        print("Checking relationships...")
        usuario = Usuario()
        print(f"Usuario.ativo exists: {hasattr(usuario, 'ativo')}")
        print(f"Usuario.check_password exists: {hasattr(usuario, 'check_password')}")
        print(f"Usuario.verificar_senha exists: {hasattr(usuario, 'verificar_senha')}")
        
        assert hasattr(usuario, 'ativo'), "Usuario.ativo missing"
        assert hasattr(usuario, 'check_password'), "Usuario.check_password missing"
        
        print("All models verified successfully!")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
