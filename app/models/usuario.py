"""
Modelo de Usuário
"""

from datetime import datetime
from app.models import db, bcrypt


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=True) # UUID
    
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    
    is_admin = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True) # Added missing field
    
    # Address info found in DB schema
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    endereco = db.Column(db.String(255)) # Added missing field
    cep = db.Column(db.String(10)) # Added missing field
    data_nascimento = db.Column(db.Date) # Added missing field
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Reset de Senha
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)

    # Relationships are backrefs from Compra/Campanha, but we can define explicit ones if needed.
    # purchases = db.relationship('Compra', back_populates='usuario') 
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

    def set_password(self, password):
        self.senha_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.senha_hash, password)

    # Alias for compatibility if needed, but controller now uses check_password
    def verificar_senha(self, password):
         return self.check_password(password)

    def generate_reset_token(self):
        """Gera um token de recuperação de senha válido por 15 minutos"""
        import uuid
        from datetime import datetime, timedelta
        
        self.reset_token = str(uuid.uuid4())
        self.reset_token_expiration = datetime.utcnow() + timedelta(minutes=15)
        return self.reset_token

    def is_reset_token_valid(self, token):
        """Verifica se o token é válido e não expirou"""
        from datetime import datetime
        
        if self.reset_token != token:
            return False
            
        if self.reset_token_expiration < datetime.utcnow():
            return False
            
        return True

    def to_dict(self):
        """Serializa o objeto para dicionário (CAMUFLADO)"""
        # Mascarar e-mail
        masked_email = None
        if self.email:
            name, domain = self.email.split("@")
            masked_email = f"{name[:2]}***@{domain}"

        # Mascarar CPF
        masked_cpf = None
        if self.cpf:
            masked_cpf = f"***.***.***-{self.cpf[-2:]}"

        return {
            'id': self.public_id, # Public ID
            'nome': self.nome,
            'telefone': self.telefone, # Telefone é menos sensível para o próprio user, mas para outros deve ser escondido
            'email': masked_email,
            'cpf': masked_cpf,
            'cidade': self.cidade,
            'estado': self.estado,
            'is_admin': self.is_admin,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }
