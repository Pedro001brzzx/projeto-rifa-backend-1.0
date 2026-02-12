"""
Modelo de Usuário
"""

from datetime import datetime
from app.models import db, bcrypt


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date)
    endereco = db.Column(db.String(255))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    is_admin = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    compras = db.relationship('Compra', back_populates='usuario', lazy='dynamic')
    
    def set_senha(self, senha):
        """Define a senha do usuário com hash bcrypt"""
        self.senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
    
    def verificar_senha(self, senha):
        """Verifica se a senha fornecida está correta"""
        return bcrypt.check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        """Serializa o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'email': self.email,
            'cpf': self.cpf,
            'cidade': self.cidade,
            'estado': self.estado,
            'is_admin': self.is_admin,
            'criado_em': self.criado_em.isoformat()
        }
