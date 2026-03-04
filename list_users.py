from app import create_app
from app.models import Usuario

app = create_app()

with app.app_context():
    users = Usuario.query.all()
    print(f"Encontrados {len(users)} usuários:")
    for u in users:
        print(f"ID: {u.id} | Nome: {u.nome} | Email: {u.email} | Admin: {u.is_admin} | CPF: {u.cpf}")
