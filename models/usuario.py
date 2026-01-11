from datetime import date
from app.extensions import db, bcrypt
from .base import BaseModel

class Usuario(BaseModel):
    __tablename__ = 'usuarios'

    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)

    cpf = db.Column(db.String(14), unique=True)
    data_nascimento = db.Column(db.Date)
    endereco = db.Column(db.String(255))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    cep = db.Column(db.String(10))

    is_admin = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    compras = db.relationship(
        'Compra',
        back_populates='usuario',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_senha(self, senha: str):
        self.senha_hash = bcrypt.generate_password_hash(senha).decode()

    def verificar_senha(self, senha: str) -> bool:
        return bcrypt.check_password_hash(self.senha_hash, senha)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'email': self.email,
            'cidade': self.cidade,
            'estado': self.estado,
            'is_admin': self.is_admin,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat()
        }
