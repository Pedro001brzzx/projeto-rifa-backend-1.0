from app.extensions import db
from .base import BaseModel

class Compra(BaseModel):
    __tablename__ = 'compras'

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    campanha_id = db.Column(db.Integer, db.ForeignKey('campanhas.id'), nullable=False)

    quantidade_titulos = db.Column(db.Integer, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)

    status_pagamento = db.Column(db.String(20), default='pendente')
    metodo_pagamento = db.Column(db.String(50))
    transacao_id = db.Column(db.String(100))
    data_pagamento = db.Column(db.DateTime)
    expira_em = db.Column(db.DateTime)  # Prazo para pagamento (10 minutos)

    usuario = db.relationship('Usuario', back_populates='compras')
    campanha = db.relationship('Campanha', back_populates='compras')

    titulos = db.relationship(
        'Titulo',
        back_populates='compra',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'valor_total': float(self.valor_total),
            'status_pagamento': self.status_pagamento,
            'quantidade_titulos': self.quantidade_titulos,
            'criado_em': self.criado_em.isoformat(),
            'expira_em': self.expira_em.isoformat() if self.expira_em else None,
            'titulos': [t.to_dict() for t in self.titulos]
        }
