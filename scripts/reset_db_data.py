
import sys
import os

# Adiciona o diretório raiz ao path para importar o app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, Compra, Titulo, Campanha

# Criar instância da aplicação
app = create_app('default')

def reset_data():
    with app.app_context():
        print("🗑️  Iniciando reset de dados de compras e títulos...")
        
        # 1. Deletar todos os tickets
        try:
            num_titulos = db.session.query(Titulo).delete()
            print(f"✅ {num_titulos} títulos removidos.")
        except Exception as e:
            print(f"❌ Erro ao deletar títulos: {e}")
            db.session.rollback()
            return

        # 2. Deletar todas as compras
        try:
            num_compras = db.session.query(Compra).delete()
            print(f"✅ {num_compras} compras removidas.")
        except Exception as e:
            print(f"❌ Erro ao deletar compras: {e}")
            db.session.rollback()
            return
            
        # 3. Resetar contadores das campanhas
        try:
            campanhas = Campanha.query.all()
            for campanha in campanhas:
                campanha.titulos_vendidos = 0
                # Se houver campo explícito de disponíveis, resetar também
                # (geralmente é calculado, mas se for persistido, atualizar aqui)
                # campanha.titulos_disponiveis = campanha.total_titulos 
                print(f"🔄 Campanha '{campanha.titulo}': Vendidos resetados para 0.")
            
            db.session.commit()
            print("✅ Contadores de campanha atualizados (commit realizado).")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar campanhas: {e}")
            db.session.rollback()
            return

        print("\n✨ Reset concluído com sucesso! O banco está limpo para a nova lógica de títulos.")

if __name__ == "__main__":
    print("⚠️  ATENÇÃO: Modo automático (agente). Resetando dados...")
    reset_data()
