from app.extensions import db
from .base import BaseModel

class Comunicado(BaseModel):
    __tablename__ = 'comunicados'

    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50))
    ativo = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'tipo': self.tipo,
            'criado_em': self.criado_em.isoformat()
        }
