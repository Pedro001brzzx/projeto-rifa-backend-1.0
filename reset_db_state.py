from app import create_app
from app.models import db, Usuario, Campanha, Compra, Titulo
from datetime import datetime, timedelta
import uuid

app = create_app()

with app.app_context():
    print("🔄 Iniciando reset do banco de dados (preservando Usuário ID 4)...")

    # 1. Deletar dados na ordem de dependência (filhos primeiro)
    print("🗑️ Deletando Títulos...")
    Titulo.query.delete()
    
    print("🗑️ Deletando Compras...")
    Compra.query.delete()
    
    print("🗑️ Deletando Campanhas...")
    Campanha.query.delete()
    
    # Opcional: Deletar outros usuários se existirem (preservando ID 4)
    # Usuario.query.filter(Usuario.id != 4).delete()
    
    db.session.commit()
    print("✅ Dados limpos!")

    # 2. Criar nova campanha de teste
    print("🆕 Criando Campanha de Teste...")
    nova_campanha = Campanha(
        public_id=str(uuid.uuid4()),
        titulo="Campanha de Teste Rápido ⚡",
        descricao="Campanha criada automaticamente para validação do fluxo de checkout.",
        slug="campanha-teste-rapido",
        imagem_principal="/placeholder-campaign.jpg", # Placeholder image
        valor_titulo=0.10, # Barato para teste
        total_titulos=100, # Pequena para teste
        titulos_vendidos=0,
        data_sorteio=datetime.utcnow() + timedelta(days=7),
        status='ativo',
        tipo='automatico',
        min_quantidade_compra=1,
        max_quantidade_compra=50,
        criado_em=datetime.utcnow()
    )
    
    db.session.add(nova_campanha)
    db.session.commit()
    
    print(f"✅ Campanha criada com sucesso!")
    print(f"🆔 ID: {nova_campanha.id}")
    print(f"🔗 Public ID: {nova_campanha.public_id}")
    print(f"🐌 Slug: {nova_campanha.slug}")
    print("\n🚀 Reset concluído! O sistema está pronto para testes.")
