"""
Modelo de Comunicado
"""

from datetime import datetime, timezone
from app.models import db

_UTC = timezone.utc


class Comunicado(db.Model):
    __tablename__ = 'comunicados'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50))  # informativo, alerta, aviso
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(_UTC).replace(tzinfo=None))
    
    def to_dict(self):
        """Serializa o objeto para dicionário"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'tipo': self.tipo,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat()
        }
