"""
Modelo de Compra
"""

from datetime import datetime
from app.models import db


class Compra(db.Model):
    __tablename__ = 'compras'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=True) # UUID
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    # ... (other fields)

    def to_dict(self):
        """Serializa o objeto para dicionário (CAMUFLADO)"""
        return {
            'id': self.public_id, # Public ID instead of internal ID
            # 'internal_id': self.id, # NEVER EXPOSE
            'campanha': self.campanha.to_dict(include_stats=False) if self.campanha else None, # Don't show stats in purchase view
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
