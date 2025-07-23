from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.budget import Budget
from app import db
from datetime import datetime

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/orcamentos', methods=['POST'])
@jwt_required()
def criar_orcamento():
    dados = request.get_json()
    nome = dados.get('nome')
    valor_total = dados.get('valor_total')
    user_id = get_jwt_identity()
    if not nome or valor_total is None:
        return jsonify({'msg': 'Nome e valor_total são obrigatórios'}), 400
    orcamento = Budget(user_id=user_id, nome=nome, valor_total=valor_total)
    db.session.add(orcamento)
    db.session.commit()
    return jsonify({'msg': 'Orçamento criado com sucesso', 'id': orcamento.id}), 201

@budget_bp.route('/orcamentos', methods=['GET'])
@jwt_required()
def listar_orcamentos():
    user_id = get_jwt_identity()
    orcamentos = Budget.query.filter_by(user_id=user_id).order_by(Budget.criado_em.desc()).all()
    return jsonify([
        {
            'id': o.id,
            'nome': o.nome,
            'valor_total': o.valor_total,
            'criado_em': o.criado_em.strftime('%Y-%m-%d %H:%M')
        } for o in orcamentos
    ])
