from app import db

def init_db():
    db.create_all()
    print('Banco de dados inicializado!')

if __name__ == '__main__':
    init_db()
