from app import db

class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    contato = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(255)) 