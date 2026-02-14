
from functools import wraps
from flask import request
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models.admin_log import AdminLog
from app.models.usuario import Usuario

def log_admin_action(action, details=None):
    """
    Registra uma ação administrativa no banco deados
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return

        # Tenta obter IP de headers comuns de proxy
        if request.headers.getlist("X-Forwarded-For"):
            ip_address = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip_address = request.remote_addr

        log_entry = AdminLog(
            admin_id=int(user_id),
            action=action,
            details=str(details) if details else None,
            ip_address=ip_address,
            user_agent=request.user_agent.string
        )
        
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        # Falha no log não deve parar a aplicação, mas deve ser notada
        print(f"❌ Error logging admin action: {e}")
        db.session.rollback()

def with_admin_log(action_name):
    """
    Decorador para registrar automaticamente ações de rotas
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Executa a função original
            result = fn(*args, **kwargs)
            
            # Log após execução bem sucedida (ou tenta)
            # Nota: se a função original retornar erro, deve-se decidir se loga ou não.
            # Aqui logamos apenas se não houver exceção não tratada.
            
            # Detalhes podem ser enriquecidos se necessário
            log_admin_action(action_name, details=f"Args: {kwargs}")
            
            return result
        return wrapper
    return decorator
