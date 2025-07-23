try:
    from apscheduler.schedulers.background import BackgroundScheduler
except ImportError:
    BackgroundScheduler = None
from app import db
from models.user import User
from services.ia_service import swot_from_db, buscar_tendencias_mercado

def enviar_relatorio_semanal():
    for user in User.query.all():
        swot = swot_from_db(user.id, db)
        tendencias = buscar_tendencias_mercado("tecnologia")
ro para {user.nome}: SWOT={swot}, Tendências={tendencias}") 

        # Só inicializa o scheduler se o BackgroundScheduler foi importado corretamente
if BackgroundScheduler is not None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(enviar_relatorio_semanal, 'interval', weeks=1)
    scheduler.start()