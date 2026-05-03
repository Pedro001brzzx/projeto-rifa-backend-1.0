"""
Modelo de Contato
"""

from datetime import datetime, timezone
from app.models import db

_UTC = timezone.utc


class Contato(db.Model):
    __tablename__ = 'contatos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20))
    assunto = db.Column(db.String(200))
    mensagem = db.Column(db.Text, nullable=False)
    respondido = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(_UTC).replace(tzinfo=None))
    
    def to_dict(self):
        """Serializa o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'assunto': self.assunto,
            'mensagem': self.mensagem,
            'respondido': self.respondido,
            'criado_em': self.criado_em.isoformat()
        }
