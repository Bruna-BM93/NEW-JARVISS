from app import db
from datetime import datetime
import uuid

class LeadWhatsapp(db.Model):
    __tablename__ = 'leads_whatsapp'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(255))
    telefone = db.Column(db.String(20), nullable=False)
    mensagem = db.Column(db.Text)
    tipo_conteudo = db.Column(db.String(20))  # texto, imagem, audio, etc.
    arquivo_url = db.Column(db.Text)
    data_recebida = db.Column(db.DateTime, default=datetime.utcnow)
    origem = db.Column(db.String(50), default='whatsapp')
    status = db.Column(db.String(50), default='novo')
