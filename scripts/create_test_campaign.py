import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Campanha
from datetime import datetime

app = create_app()

with app.app_context():
    # Verificar se já existe
    if Campanha.query.first():
        print("✅ Já existem campanhas no banco.")
    else:
        print("➕ Criando campanha de teste...")
        campanha = Campanha(
            titulo="Campanha Debug",
            descricao="Campanha para teste de checkout",
            imagem_principal="https://via.placeholder.com/300",
            data_sorteio=datetime.utcnow(),
            valor_titulo=10.0,
            total_titulos=1000,
            titulos_vendidos=0,
            status='ativa',
            destaque=True
        )
        db.session.add(campanha)
        db.session.commit()
        print(f"✅ Campanha criada com ID: {campanha.id}")
