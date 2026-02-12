from app import create_app, db
from app.models import Compra
import os

app = create_app()
with app.app_context():
    c = Compra.query.order_by(Compra.id.desc()).first()
    if c:
        print(f"ID: {c.id}")
        print(f"Pix Copia e Cola: {c.pix_copia_cola[:50] if c.pix_copia_cola else 'Vazio'}")
        print(f"QR Code Base64 Length: {len(c.pix_qr_code_base64) if c.pix_qr_code_base64 else 'Vazio'}")
        if c.pix_qr_code_base64:
            print(f"QR Code Starts with: {c.pix_qr_code_base64[:20]}")
    else:
        print("Nenhuma compra encontrada.")
