from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from models.cliente import Cliente
import logging
from marshmallow import Schema, fields, ValidationError

cliente_bp = Blueprint('cliente', __name__)

class ClienteSchema(Schema):
    nome = fields.String(required=True)
    email = fields.String()
    telefone = fields.String()
    endereco = fields.String()

@cliente_bp.route('/clientes', methods=['POST'])
@jwt_required()
def cadastrar_cliente():
    try:
        dados = request.get_json()
        schema = ClienteSchema()
        try:
            validado = schema.load(dados)
        except ValidationError as err:
            return jsonify({'erro': 'Dados inválidos', 'detalhes': err.messages}), 400
        cliente = Cliente(**validado)
        db.session.add(cliente)
        db.session.commit()
        return jsonify({'msg': 'Cliente cadastrado com sucesso', 'id': cliente.id}), 201
    except Exception as e:
        logging.exception('Erro ao cadastrar cliente')
        return jsonify({'erro': 'Erro interno ao cadastrar cliente', 'detalhe': str(e)}), 500

@cliente_bp.route('/clientes', methods=['GET'])
@jwt_required()
def listar_clientes():
    try:
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
        except ValueError:
            page, per_page = 1, 10
        query = Cliente.query.with_entities(
            Cliente.id, Cliente.nome, Cliente.email, Cliente.telefone, Cliente.endereco
        )
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        clientes = paginated.items
        return jsonify([
            {
                'id': c.id,
                'nome': c.nome,
                'email': c.email,
                'telefone': c.telefone,
                'endereco': c.endereco
            } for c in clientes
        ])
    except Exception as e:
        logging.exception('Erro ao listar clientes')
        return jsonify({'erro': 'Erro interno ao listar clientes', 'detalhe': str(e)}), 500 