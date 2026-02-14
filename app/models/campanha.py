"""
Modelo de Campanha
"""

from datetime import datetime
from app.models import db


class Campanha(db.Model):
    __tablename__ = 'campanhas'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=True) # UUID
    titulo = db.Column(db.String(200), nullable=False)
    # ... (other code)

    def to_dict(self, include_stats=False):
        """Serializa o objeto para dicionário (CAMUFLADO)"""
        data = {
            'id': self.public_id, # Public ID (UUID)
            #'internal_id': self.id, # NEVER EXPOSE THIS
            'titulo': self.titulo,
            'descricao': self.descricao,
            'slug': self.slug,
            'imagem_principal': self.imagem_principal,
            'status': self.status,
            'tipo': self.tipo,
            'premio': self.premio,
            'valor_titulo': float(self.valor_titulo) if self.valor_titulo else None,
            'min_quantidade_compra': self.min_quantidade_compra,
            'max_quantidade_compra': self.max_quantidade_compra,
            'data_sorteio': (self.data_sorteio.isoformat() + 'Z') if self.data_sorteio else None,
            'criado_em': self.criado_em.isoformat() + 'Z',
        }
        
        if include_stats:
            # CAMOUFLAGE: Show progress instead of raw counts
            total = self.total_titulos or 0
            vendidos = self.titulos_vendidos or 0
            
            percentual = (vendidos / total * 100) if total > 0 else 0
            
            data['progresso'] = round(percentual, 2)
            # data['total_titulos'] = total # HIDDEN
            # data['titulos_vendidos'] = vendidos # HIDDEN
        
        if self.ganhador:
            data['ganhador'] = {
                'nome': self.ganhador.nome.split()[0] + ' ***', # Masked name
                'cidade': self.ganhador.cidade,
                'estado': self.ganhador.estado
            }
            
        return data
