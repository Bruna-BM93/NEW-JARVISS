from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from models.fornecedor import Fornecedor
import logging
from marshmallow import Schema, fields, ValidationError

fornecedor_bp = Blueprint('fornecedor', __name__)

class FornecedorSchema(Schema):
    nome = fields.String(required=True)
    contato = fields.String()
    telefone = fields.String()
    endereco = fields.String()

@fornecedor_bp.route('/fornecedores', methods=['POST'])
@jwt_required()
def cadastrar_fornecedor():
    try:
        dados = request.get_json()
        schema = FornecedorSchema()
        try:
            validado = schema.load(dados)
        except ValidationError as err:
            return jsonify({'erro': 'Dados inválidos', 'detalhes': err.messages}), 400
        fornecedor = Fornecedor(**validado)
        db.session.add(fornecedor)
        db.session.commit()
        return jsonify({'msg': 'Fornecedor cadastrado com sucesso', 'id': fornecedor.id}), 201
    except Exception as e:
        logging.exception('Erro ao cadastrar fornecedor')
        return jsonify({'erro': 'Erro interno ao cadastrar fornecedor', 'detalhe': str(e)}), 500

@fornecedor_bp.route('/fornecedores', methods=['GET'])
@jwt_required()
def listar_fornecedores():
    try:
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
        except ValueError:
            page, per_page = 1, 10
        query = Fornecedor.query.with_entities(
            Fornecedor.id, Fornecedor.nome, Fornecedor.contato, Fornecedor.telefone, Fornecedor.endereco
        )
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        fornecedores = paginated.items
        return jsonify([
            {
                'id': f.id,
                'nome': f.nome,
                'contato': f.contato,
                'telefone': f.telefone,
                'endereco': f.endereco
            } for f in fornecedores
        ])
    except Exception as e:
        logging.exception('Erro ao listar fornecedores')
        return jsonify({'erro': 'Erro interno ao listar fornecedores', 'detalhe': str(e)}), 500 