from app.extensions import db
from .base import BaseModel

class Titulo(BaseModel):
    __tablename__ = 'titulos'

    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    is_ganhador = db.Column(db.Boolean, default=False)

    compra = db.relationship('Compra', back_populates='titulos')

    __table_args__ = (
        db.UniqueConstraint('numero', 'compra_id', name='uq_titulo_numero_compra'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'is_ganhador': self.is_ganhador
        }
