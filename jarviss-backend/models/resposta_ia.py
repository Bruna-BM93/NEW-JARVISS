from app import db
from datetime import datetime

class RespostaIA(db.Model):
    __tablename__ = 'respostas_ia'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    plano = db.Column(db.String(20), nullable=False)
    pergunta = db.Column(db.Text, nullable=False)
    resposta = db.Column(db.Text, nullable=False) 