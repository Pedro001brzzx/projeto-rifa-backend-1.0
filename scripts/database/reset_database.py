"""
Script para resetar banco de dados e criar dados de teste
"""

import sys
import os

# Add parent directory to Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
import os
from app import create_app
from app.models import db, Usuario, Campanha, Compra, Titulo
from datetime import datetime

def reset_database():
    """Deleta e recria o banco de dados"""
    app = create_app()
    
    with app.app_context():
        print("\n🗑️  Deletando banco de dados antigo...")
        
        # Deletar arquivo do banco (SQLite)
        db_path = 'instance/rifas.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Banco deletado!")
        else:
            print("⚠️  Banco não encontrado (será criado)")
        
        print("\n🔨 Criando novo banco de dados...")
        db.create_all()
        print("✅ Tabelas criadas!")
        
        print("\n👤 Criando usuário de teste...")
        usuario = Usuario(
            nome="Pedro Henrique",
            cpf="00011122233",
            telefone="5583994099696",
            is_admin=True
        )
        usuario.set_senha("123456")
        db.session.add(usuario)
        db.session.flush()
        print(f"✅ Usuário criado: {usuario.nome} (ID: {usuario.id})")
        
        print("\n🎯 Criando campanha de teste...")
        campanha = Campanha(
            titulo="Notebook Gamer RTX 4060",
            slug="notebook-gamer-rtx-4060",
            descricao="Notebook Gamer de última geração com RTX 4060",
            imagem_principal="https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800",
            valor_titulo=5.00,
            total_titulos=10000,
            titulos_vendidos=0,
            status='ativo',
            data_inicio=datetime.utcnow()
        )
        db.session.add(campanha)
        db.session.flush()
        print(f"✅ Campanha criada: {campanha.titulo} (ID: {campanha.id})")
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ BANCO DE DADOS RESETADO COM SUCESSO!")
        print("="*60)
        print("\n📋 Dados de login:")
        print(f"   Telefone: 5583994099696")
        print(f"   Senha: 123456")
        print(f"\n🎯 Campanha disponível:")
        print(f"   {campanha.titulo}")
        print(f"   Slug: {campanha.slug}")
        print("\n")

if __name__ == '__main__':
    reset_database()
