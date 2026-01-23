"""
Configuração do APScheduler para limpeza de compras expiradas
"""

from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs.cleanup_expired_purchases import cancelar_compras_expiradas
import atexit

scheduler = None

def init_scheduler(app):
    """
    Inicializa o scheduler de tarefas em background
    Deve ser chamado apenas no processo principal do Flask
    """
    global scheduler
    
    # Prevenir duplicação no modo debug (reloader)
    if app.debug and not app.config.get('WERKZEUG_RUN_MAIN'):
        return
    
    if scheduler is None:
        scheduler = BackgroundScheduler(daemon=True)
        
        # Adicionar job de limpeza de compras expiradas
        scheduler.add_job(
            func=cancelar_compras_expiradas,
            trigger="interval",
            minutes=1,  # Executa a cada 1 minuto
            id='cleanup_expired_purchases',
            name='Limpar compras expiradas',
            replace_existing=True
        )
        
        scheduler.start()
        
        # Registrar shutdown limpo
        atexit.register(lambda: scheduler.shutdown() if scheduler else None)
        
        with app.app_context():
            print("✅ APScheduler iniciado - Limpeza de compras a cada 1 minuto")
