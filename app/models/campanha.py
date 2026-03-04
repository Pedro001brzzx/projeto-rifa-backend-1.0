"""
Modelo de Campanha
"""

from datetime import datetime, date
from app.models import db


class Campanha(db.Model):
    __tablename__ = 'campanhas'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=True) # UUID
    
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    imagem_principal = db.Column(db.String(500))
    codigo = db.Column(db.String(50))
    tipo = db.Column(db.String(50)) # 'automatico' ou 'manual'
    premio = db.Column(db.String(200))
    valor_titulo = db.Column(db.Numeric(10, 2))
    
    total_titulos = db.Column(db.Integer)
    titulos_vendidos = db.Column(db.Integer, default=0)
    
    data_sorteio = db.Column(db.DateTime)
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    
    status = db.Column(db.String(20), default='ativo')
    numero_sorteado = db.Column(db.String(50))
    ganhador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    data_conclusao = db.Column(db.Date, nullable=True)
    regulamento = db.Column(db.Text)
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    min_quantidade_compra = db.Column(db.Integer, default=1)
    max_quantidade_compra = db.Column(db.Integer)

    # Relacionamentos
    ganhador = db.relationship('Usuario', foreign_keys=[ganhador_id], backref='campanhas_ganhas')
    # Titulo e Compra relationships will be defined in their respective models or via backref

    @property
    def titulos_disponiveis(self):
        """Calcula títulos disponíveis em tempo real"""
        return (self.total_titulos or 0) - (self.titulos_vendidos or 0)

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
            'data_conclusao': self.data_conclusao.strftime('%d/%m/%Y') if self.data_conclusao else None,
            'numero_sorteado': self.numero_sorteado,
            'criado_em': self.criado_em.isoformat() + 'Z',
        }
        
        if include_stats:
            # CAMOUFLAGE: Show progress instead of raw counts
            total = self.total_titulos or 0
            vendidos = self.titulos_vendidos or 0
            
            percentual = (vendidos / total * 100) if total > 0 else 0
            
            data['progresso'] = round(percentual, 2)
            
            # EXPOSED FOR FRONTEND COUNTER
            data['total_titulos'] = total
            data['titulos_vendidos'] = vendidos
            data['titulos_disponiveis'] = self.titulos_disponiveis

            # Modern Frontend Keys
            data['totalTickets'] = total
            data['soldTickets'] = vendidos
            data['availableTickets'] = self.titulos_disponiveis

        
        if self.ganhador:
            # Mask phone: (XX) XXXXX-1234 -> (**) *****-1234
            masked_phone = None
            if self.ganhador.telefone:
                phone = self.ganhador.telefone
                if len(phone) >= 4:
                    masked_phone = f'(**) *****-{phone[-4:]}'
                else:
                    masked_phone = '(**) *****-****'

            data['ganhador'] = {
                'nome': self.ganhador.nome.split()[0] + ' ***', # Masked name
                'cidade': self.ganhador.cidade,
                'estado': self.ganhador.estado,
                'telefone': masked_phone,
                'numero_sorteado': self.numero_sorteado,
                'premio': self.premio,
                'data_conclusao': self.data_conclusao.strftime('%d/%m/%Y') if self.data_conclusao else None,
            }
            
        return data
