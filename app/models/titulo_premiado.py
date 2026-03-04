"""
Modelo de Título Premiado
"""

from datetime import datetime
from app.models import db

class TituloPremiado(db.Model):
    __tablename__ = 'titulos_premiados'
    
    id = db.Column(db.Integer, primary_key=True)
    campanha_id = db.Column(db.Integer, db.ForeignKey('campanhas.id'), nullable=False)
    numero_titulo = db.Column(db.String(20), nullable=False)
    valor_premio = db.Column(db.Numeric(10, 2), nullable=False)
    ganhador_nome = db.Column(db.String(200)) # Opcional, preenchido quando houver ganhador
    ganhador_usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    status = db.Column(db.String(20), default='disponivel') # disponivel, ganho
    data_sorteio = db.Column(db.DateTime)
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    campanha = db.relationship('Campanha', backref=db.backref('titulos_premiados', lazy=True))
    ganhador = db.relationship('Usuario', foreign_keys=[ganhador_usuario_id])

    def to_dict(self):
        """Serializa o objeto para dicionário"""
        data = {
            'id': self.id,
            'campanha_id': self.campanha.public_id if self.campanha else None,
            'numero_titulo': self.numero_titulo,
            'valor_premio': float(self.valor_premio) if self.valor_premio else 0.0,
            'status': self.status,
            'data_sorteio': (self.data_sorteio.isoformat() + 'Z') if self.data_sorteio else None,
            'criado_em': self.criado_em.isoformat() + 'Z'
        }
        
        if self.ganhador_nome:
             # Mask name: "João Silva" -> "João S***"
             try:
                 parts = self.ganhador_nome.split()
                 masked = parts[0] + ' ' + (parts[1][0] + '***' if len(parts) > 1 else '***')
                 data['ganhador_nome'] = masked
             except:
                 data['ganhador_nome'] = '***'
        else:
            data['ganhador_nome'] = None
            
        return data
