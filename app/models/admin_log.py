
from datetime import datetime
from app.extensions import db

class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True) # IPv6 support
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    admin = db.relationship('Usuario', foreign_keys=[admin_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'admin_name': self.admin.nome if self.admin else 'Sistema/Desconhecido',
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() + 'Z'
        }
