"""
Script para adicionar campanhas de exemplo ao banco de dados
Execute: python adicionar_campanhas.py
"""

from datetime import datetime, timedelta
from app import create_app
from app.models import db, Campanha

# Criar aplicação
app = create_app()

# Campanhas de exemplo com imagens
campanhas_exemplo = [
    {
        'titulo': 'iPhone 15 Pro Max 256GB',
        'descricao': 'Concorra a um iPhone 15 Pro Max 256GB novo, zero km, na cor azul titânio. Sorteio pela Loteria Federal!',
        'slug': 'iphone-15-pro-max-janeiro-2026',
        'imagem_principal': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800',
        'codigo': 'RIFA001',
        'tipo': 'regular',
        'premio': 'iPhone 15 Pro Max 256GB',
        'valor_titulo': 10.00,
        'total_titulos': 5000,
        'data_sorteio': "Quando o Número de cotas for finalizado",
        'regulamento': '1. Sorteio pela Loteria Federal\n2. Mínimo 80% dos títulos vendidos\n3. Prêmio entregue em até 7 dias',
        'status': 'ativo'
    },
    {
        'titulo': 'Notebook Gamer RTX 4060',
        'descricao': 'Notebook Gamer top de linha: Intel i7, 16GB RAM, RTX 4060, SSD 512GB. Perfeito para jogos e trabalho!',
        'slug': 'notebook-gamer-rtx-4060',
        'imagem_principal': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800',
        'codigo': 'RIFA002',
        'tipo': 'regular',
        'premio': 'Notebook Gamer Acer Nitro 5',
        'valor_titulo': 15.00,
        'total_titulos': 3000,
        'data_sorteio': "Quando o Número de cotas for finalizado",
        'regulamento': '1. Sorteio pela Loteria Federal\n2. Mínimo 70% dos títulos vendidos\n3. Prêmio entregue em até 15 dias',
        'status': 'ativo'
    },
    {
        'titulo': 'Kit Churrasco Premium',
        'descricao': 'Kit completo para churrasco: Churrasqueira Elétrica Weber + Conjunto de facas profissionais + Avental personalizado!',
        'slug': 'kit-churrasco-premium',
        'imagem_principal': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800',
        'codigo': 'RIFA003',
        'tipo': 'especial',
        'premio': 'Kit Churrasco Completo',
        'valor_titulo': 5.00,
        'total_titulos': 2000,
        'data_sorteio': "Quando o Número de cotas for finalizado",
        'regulamento': '1. Sorteio pela Loteria Federal\n2. Mínimo 60% dos títulos vendidos',
        'status': 'ativo'
    },
    {
        'titulo': 'PlayStation 5 + 2 Controles',
        'descricao': 'PlayStation 5 novo com 2 controles DualSense + God of War Ragnarök. A melhor experiência em jogos!',
        'slug': 'playstation-5-completo',
        'imagem_principal': 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800',
        'codigo': 'RIFA004',
        'tipo': 'regular',
        'premio': 'PlayStation 5 + 2 Controles + Jogo',
        'valor_titulo': 12.00,
        'total_titulos': 4000,
        'data_sorteio': "Quando o Número de cotas for finalizado",
        'regulamento': '1. Sorteio pela Loteria Federal\n2. Console novo lacrado\n3. Entrega em até 10 dias',
        'status': 'ativo'
    },
    {
        'titulo': 'Smart TV 55" 4K Samsung',
        'descricao': 'Smart TV Samsung 55 polegadas 4K UHD, com tecnologia Crystal Display e sistema Tizen. Imagem perfeita!',
        'slug': 'smart-tv-samsung-55-4k',
        'imagem_principal': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800',
        'codigo': 'RIFA005',
        'tipo': 'regular',
        'premio': 'Smart TV Samsung 55" 4K',
        'valor_titulo': 8.00,
        'total_titulos': 3500,
        'data_sorteio': "Quando o Número de cotas for finalizado",
        'regulamento': '1. Sorteio pela Loteria Federal\n2. TV nova na caixa\n3. Garantia de 1 ano',
        'status': 'ativo'
    }
]

def adicionar_campanhas():
    """Adiciona campanhas de exemplo ao banco de dados"""
    with app.app_context():
        print("🎯 Adicionando campanhas ao banco de dados...\n")
        
        campanhas_adicionadas = 0
        campanhas_existentes = 0
        
        for dados in campanhas_exemplo:
            # Verificar se já existe pelo slug
            campanha_existe = Campanha.query.filter_by(slug=dados['slug']).first()
            
            if campanha_existe:
                print(f"⚠️  Campanha já existe: {dados['titulo']}")
                campanhas_existentes += 1
                continue
            
            # Criar nova campanha
            campanha = Campanha(**dados)
            db.session.add(campanha)
            
            print(f"✅ Adicionada: {dados['titulo']}")
            print(f"   📷 Imagem: {dados['imagem_principal'][:50]}...")
            print(f"   💰 Valor: R$ {dados['valor_titulo']:.2f}")
            print(f"   🎫 Títulos: {dados['total_titulos']}")
            print(f"   📅 Sorteio: {dados['data_sorteio'].strftime('%d/%m/%Y')}")
            print()
            
            campanhas_adicionadas += 1
        
        # Salvar no banco
        db.session.commit()
        
        print("="*60)
        print(f"🎉 Processo concluído!")
        print(f"✅ Campanhas adicionadas: {campanhas_adicionadas}")
        print(f"⚠️  Campanhas já existentes: {campanhas_existentes}")
        print(f"📊 Total no banco: {Campanha.query.count()}")
        print("="*60)

if __name__ == '__main__':
    adicionar_campanhas()
