from app.extensions import db
from .base import BaseModel

class Contato(BaseModel):
    __tablename__ = 'contatos'

    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20))
    assunto = db.Column(db.String(200))
    mensagem = db.Column(db.Text, nullable=False)
    respondido = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'respondido': self.respondido,
            'criado_em': self.criado_em.isoformat()
        }
