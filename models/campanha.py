from app.extensions import db
from .base import BaseModel

class Campanha(BaseModel):
    __tablename__ = 'campanhas'

    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    slug = db.Column(db.String(255), unique=True, nullable=False)

    imagem_principal = db.Column(db.String(500))
    codigo = db.Column(db.String(50), unique=True)

    tipo = db.Column(db.String(50), default='regular')
    premio = db.Column(db.String(200))

    valor_titulo = db.Column(db.Numeric(10, 2))
    total_titulos = db.Column(db.Integer)
    titulos_vendidos = db.Column(db.Integer, default=0)

    data_inicio = db.Column(db.DateTime)
    data_fim = db.Column(db.DateTime)
    data_sorteio = db.Column(db.DateTime)

    status = db.Column(db.String(20), default='ativo')

    numero_sorteado = db.Column(db.String(50))
    ganhador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    regulamento = db.Column(db.Text)

    compras = db.relationship(
        'Compra',
        back_populates='campanha',
        cascade='all, delete-orphan'
    )

    ganhador = db.relationship('Usuario', foreign_keys=[ganhador_id])

    def percentual_vendido(self):
        if not self.total_titulos:
            return 0
        return round((self.titulos_vendidos / self.total_titulos) * 100, 2)

    def to_dict(self, include_stats=False):
        data = {
            'id': self.id,
            'titulo': self.titulo,
            'slug': self.slug,
            'premio': self.premio,
            'valor_titulo': float(self.valor_titulo) if self.valor_titulo else None,
            'status': self.status,
            'data_sorteio': self.data_sorteio.isoformat() if self.data_sorteio else None,
        }

        if include_stats:
            data.update({
                'total_titulos': self.total_titulos,
                'titulos_vendidos': self.titulos_vendidos,
                'percentual_vendido': self.percentual_vendido()
            })

        if self.ganhador:
            data['ganhador'] = {
                'nome': self.ganhador.nome,
                'cidade': self.ganhador.cidade,
                'estado': self.ganhador.estado
            }

        return data
