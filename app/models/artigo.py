"""
Modelo de Artigo
"""

from datetime import datetime, timezone
from app.models import db

_UTC = timezone.utc


class Artigo(db.Model):
    __tablename__ = 'artigos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    conteudo = db.Column(db.Text)
    imagem = db.Column(db.String(500))
    autor = db.Column(db.String(100))
    publicado = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(_UTC).replace(tzinfo=None))
    atualizado_em = db.Column(db.DateTime, onupdate=lambda: datetime.now(_UTC).replace(tzinfo=None))
    
    def to_dict(self):
        """Serializa o objeto para dicionário"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'slug': self.slug,
            'conteudo': self.conteudo,
            'imagem': self.imagem,
            'autor': self.autor,
            'criado_em': self.criado_em.isoformat()
        }
