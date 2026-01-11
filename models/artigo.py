from app.extensions import db
from .base import BaseModel

class Artigo(BaseModel):
    __tablename__ = 'artigos'

    titulo = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    conteudo = db.Column(db.Text)
    imagem = db.Column(db.String(500))
    autor = db.Column(db.String(100))
    publicado = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'slug': self.slug,
            'autor': self.autor,
            'criado_em': self.criado_em.isoformat()
        }
