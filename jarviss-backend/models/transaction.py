from app import db
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # receita ou despesa
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255))
    data = db.Column(db.Date, default=datetime.utcnow)
