"""
Modelo de Campanha
"""

from datetime import datetime
from app.models import db


class Campanha(db.Model):
    __tablename__ = 'campanhas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    imagem_principal = db.Column(db.String(500))
    codigo = db.Column(db.String(50), unique=True)
    tipo = db.Column(db.String(50))  # 'select', 'regular'
    premio = db.Column(db.String(200))
    valor_titulo = db.Column(db.Numeric(10, 2))
    total_titulos = db.Column(db.Integer)
    titulos_vendidos = db.Column(db.Integer, default=0)
    min_quantidade_compra = db.Column(db.Integer, default=1)  # Quantidade mínima por compra
    max_quantidade_compra = db.Column(db.Integer, nullable=True)  # Quantidade máxima por compra (NULL = sem limite)
    data_sorteio = db.Column(db.DateTime)
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='ativo')  # ativo, concluido, cancelado
    numero_sorteado = db.Column(db.String(50))
    ganhador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    regulamento = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relacionamentos
    compras = db.relationship('Compra', back_populates='campanha', lazy='dynamic')
    ganhador = db.relationship('Usuario', foreign_keys=[ganhador_id])
    
    def to_dict(self, include_stats=False):
        """Serializa o objeto para dicionário"""
        data = {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'slug': self.slug,
            'imagem_principal': self.imagem_principal,
            'codigo': self.codigo,
            'tipo': self.tipo,
            'premio': self.premio,
            'valor_titulo': float(self.valor_titulo) if self.valor_titulo else None,
            'total_titulos': self.total_titulos,
            'titulos_vendidos': self.titulos_vendidos,
            'min_quantidade_compra': self.min_quantidade_compra,
            'max_quantidade_compra': self.max_quantidade_compra,
            'data_sorteio': (self.data_sorteio.isoformat() + 'Z') if self.data_sorteio else None,
            'status': self.status,
            'criado_em': self.criado_em.isoformat() + 'Z',
            'data_inicio': (self.data_inicio.isoformat() + 'Z') if self.data_inicio else (self.criado_em.isoformat() + 'Z'),
            'data_fim': (self.data_fim.isoformat() + 'Z') if self.data_fim else None
        }
        
        if include_stats:
            data['percentual_vendido'] = (
                self.titulos_vendidos / self.total_titulos * 100
            ) if self.total_titulos else 0
            data['titulos_disponiveis'] = (
                self.total_titulos - self.titulos_vendidos
            ) if self.total_titulos else 0
        
        if self.ganhador:
            data['ganhador'] = {
                'nome': self.ganhador.nome,
                'cidade': self.ganhador.cidade,
                'estado': self.ganhador.estado
            }
            
        return data
