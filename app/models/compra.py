"""
Modelo de Compra
"""

from datetime import datetime, timezone
from app.models import db

_UTC = timezone.utc


class Compra(db.Model):
    __tablename__ = 'compras'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=True) # UUID
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    campanha_id = db.Column(db.Integer, db.ForeignKey('campanhas.id'), nullable=False)
    
    quantidade_titulos = db.Column(db.Integer, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    
    status_pagamento = db.Column(db.String(20), default='pendente') # pendente, aprovado, cancelado, expirado
    metodo_pagamento = db.Column(db.String(50))
    transacao_id = db.Column(db.String(100))
    
    data_pagamento = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(_UTC).replace(tzinfo=None))
    expira_em = db.Column(db.DateTime) # Tempo limite para pagar
    
    pix_copia_cola = db.Column(db.Text)
    pix_qr_code_base64 = db.Column(db.Text)

    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relacionamentos
    # Usuario relationship is usually defined on Usuario or via backref here
    usuario = db.relationship('Usuario', backref=db.backref('compras', lazy=True))
    
    # Campanha relationship
    campanha = db.relationship('Campanha', backref=db.backref('compras', lazy=True))
    
    # Titulos relationship (fixes the crash: Mapping 'Mapper[Titulo(titulos)]'. Original exception was: Mapper 'Mapper[Campanha(campanhas)]' has no property 'titulos')
    titulos = db.relationship('Titulo', back_populates='compra', lazy=True)

    @staticmethod
    def get_by_public_id(public_id):
        """Busca compra pelo ID público (UUID)"""
        return Compra.query.filter_by(public_id=public_id).first()


    def to_dict(self):
        """Serializa o objeto para dicionário (CAMUFLADO)"""
        return {
            'id': self.public_id, # Public ID instead of internal ID
            # 'internal_id': self.id, # NEVER EXPOSE
            'campanha': self.campanha.to_dict(include_stats=False) if self.campanha else None, # Don't show stats in purchase view
            'quantidade_titulos': self.quantidade_titulos,
            'valor_total': float(self.valor_total) if self.valor_total else 0.0,
            'status_pagamento': self.status_pagamento,
            'metodo_pagamento': self.metodo_pagamento,
            'data_pagamento': (self.data_pagamento.isoformat() + 'Z') if self.data_pagamento else None,
            'expira_em': (self.expira_em.isoformat() + 'Z') if self.expira_em else None,
            'pix_copia_cola': self.pix_copia_cola,
            'pix_qr_code_base64': self.pix_qr_code_base64,
            'criado_em': self.criado_em.isoformat() + 'Z',
            'titulos': [t.to_dict() for t in self.titulos]
        }
