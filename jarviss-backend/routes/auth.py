from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models.user import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    cpf = data.get('cpf')
    senha = data.get('senha')

    if not all([nome, email, cpf, senha]):
        return jsonify({'msg': 'Todos os campos são obrigatórios'}), 400

    if User.query.filter((User.email == email) | (User.cpf == cpf)).first():
        return jsonify({'msg': 'E-mail ou CPF já cadastrado'}), 409

    senha_hash = generate_password_hash(senha)
    novo_usuario = User(nome=nome, email=email, cpf=cpf, senha_hash=senha_hash)
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify({'msg': 'Usuário registrado com sucesso'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email_ou_cpf = data.get('email_ou_cpf')
    senha = data.get('senha')

    if not all([email_ou_cpf, senha]):
        return jsonify({'msg': 'Email/CPF e senha são obrigatórios'}), 400

    user = User.query.filter((User.email == email_ou_cpf) | (User.cpf == email_ou_cpf)).first()
    if not user or not check_password_hash(user.senha_hash, senha):
        return jsonify({'msg': 'Credenciais inválidas'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token, 'user_id': user.id, 'nome': user.nome, 'plano': user.plano}), 200
