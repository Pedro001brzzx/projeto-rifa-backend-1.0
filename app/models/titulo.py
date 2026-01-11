"""
Modelo de Título
"""

from datetime import datetime
from app.models import db


class Titulo(db.Model):
    __tablename__ = 'titulos'
    
    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'), nullable=False)
    campanha_id = db.Column(db.Integer, db.ForeignKey('campanhas.id'), nullable=False)  # Desnormalização para performance
    numero = db.Column(db.String(20), nullable=False)
    is_ganhador = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Índices para otimização de queries
    __table_args__ = (
        db.Index('idx_titulo_numero', 'numero'),  # Busca rápida por número
        db.Index('idx_titulo_campanha', 'campanha_id'),  # Busca rápida por campanha
        db.Index('idx_titulo_campanha_numero', 'campanha_id', 'numero'),  # Busca composta (mais rápida)
        db.UniqueConstraint('campanha_id', 'numero', name='uq_campanha_numero'),  # Único por campanha
    )
    
    # Relacionamentos
    compra = db.relationship('Compra', back_populates='titulos')
    campanha = db.relationship('Campanha', foreign_keys=[campanha_id])
    
    def to_dict(self):
        """Serializa o objeto para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'is_ganhador': self.is_ganhador
        }
