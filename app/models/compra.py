"""
Modelo de Compra
"""

from datetime import datetime
from app.models import db


class Compra(db.Model):
    __tablename__ = 'compras'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    campanha_id = db.Column(db.Integer, db.ForeignKey('campanhas.id'), nullable=False)
    quantidade_titulos = db.Column(db.Integer, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    status_pagamento = db.Column(db.String(20), default='pendente')  # pendente, aprovado, cancelado
    metodo_pagamento = db.Column(db.String(50))  # pix, cartao, boleto
    transacao_id = db.Column(db.String(100))
    data_pagamento = db.Column(db.DateTime)
    expira_em = db.Column(db.DateTime, nullable=True)  # Quando a compra pendente expira (10 min)
    pix_copia_cola = db.Column(db.Text, nullable=True)
    pix_qr_code_base64 = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', back_populates='compras')
    campanha = db.relationship('Campanha', back_populates='compras')
    titulos = db.relationship('Titulo', back_populates='compra', lazy='dynamic')
    
    def to_dict(self):
        """Serializa o objeto para dicionário"""
        return {
            'id': self.id,
            'campanha': self.campanha.to_dict() if self.campanha else None,
            'quantidade_titulos': self.quantidade_titulos,
            'valor_total': float(self.valor_total),
            'status_pagamento': self.status_pagamento,
            'metodo_pagamento': self.metodo_pagamento,
            'data_pagamento': (self.data_pagamento.isoformat() + 'Z') if self.data_pagamento else None,
            'expira_em': (self.expira_em.isoformat() + 'Z') if self.expira_em else None,
            'pix_copia_cola': self.pix_copia_cola,
            'pix_qr_code_base64': self.pix_qr_code_base64,
            'criado_em': self.criado_em.isoformat() + 'Z',
            'titulos': [t.to_dict() for t in self.titulos]
        }
