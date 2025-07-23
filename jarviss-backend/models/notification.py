from app import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    plano_recomendado = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pendente')
    data = db.Column(db.DateTime, default=datetime.utcnow) 