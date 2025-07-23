from app import db
from models.transaction import Transaction

def popular_dados_exemplo(user_id):
    exemplos = [
        Transaction(user_id=user_id, tipo='receita', valor=5000, descricao='Venda de Produto A'),
        Transaction(user_id=user_id, tipo='receita', valor=3000, descricao='Venda de Produto B'),
        Transaction(user_id=user_id, tipo='despesa', valor=1200, descricao='Aluguel'),
        Transaction(user_id=user_id, tipo='despesa', valor=800, descricao='Energia'),
        Transaction(user_id=user_id, tipo='despesa', valor=500, descricao='Marketing'),
        Transaction(user_id=user_id, tipo='receita', valor=2000, descricao='Venda de Produto C'),
        Transaction(user_id=user_id, tipo='despesa', valor=400, descricao='Internet'),
    ]
    db.session.bulk_save_objects(exemplos)
    db.session.commit()

if __name__ == '__main__':
    user_id = 1  # Altere para o ID do usuário desejado
    popular_dados_exemplo(user_id)
    print('Banco populado com dados de exemplo!') 