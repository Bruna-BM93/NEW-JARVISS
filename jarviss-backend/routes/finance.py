from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.transaction import Transaction
from models.user import User
from app import db
from datetime import datetime
import csv
import io

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/transacoes', methods=['POST'])
@jwt_required()
def nova_transacao():
    dados = request.get_json()
    tipo = dados.get('tipo')
    valor = dados.get('valor')
    descricao = dados.get('descricao')
    data = dados.get('data')
    user_id = get_jwt_identity()

    if tipo not in ['receita', 'despesa'] or valor is None:
        return jsonify({'msg': 'Tipo e valor são obrigatórios'}), 400

    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date() if data else datetime.utcnow().date()
    except Exception:
        return jsonify({'msg': 'Data inválida, use YYYY-MM-DD'}), 400

    transacao = Transaction(user_id=user_id, tipo=tipo, valor=valor, descricao=descricao, data=data_obj)
    db.session.add(transacao)
    db.session.commit()
    return jsonify({'msg': 'Transação salva com sucesso'}), 201

@finance_bp.route('/transacoes', methods=['GET'])
@jwt_required()
def listar_transacoes():
    user_id = get_jwt_identity()
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    query = Transaction.query.filter_by(user_id=user_id)
    if inicio:
        try:
            inicio_data = datetime.strptime(inicio, '%Y-%m-%d').date()
            query = query.filter(Transaction.data >= inicio_data)
        except Exception:
            return jsonify({'msg': 'Data início inválida'}), 400
    if fim:
        try:
            fim_data = datetime.strptime(fim, '%Y-%m-%d').date()
            query = query.filter(Transaction.data <= fim_data)
        except Exception:
            return jsonify({'msg': 'Data fim inválida'}), 400
    transacoes = query.order_by(Transaction.data.desc()).all()
    return jsonify([
        {
            'id': t.id,
            'tipo': t.tipo,
            'valor': t.valor,
            'descricao': t.descricao,
            'data': t.data.strftime('%Y-%m-%d')
        } for t in transacoes
    ])

@finance_bp.route('/transacoes/export', methods=['GET'])
@jwt_required()
def exportar_transacoes():
    user_id = get_jwt_identity()
    formato = request.args.get('formato', 'json')
    transacoes = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.data.desc()).all()
    if formato == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'tipo', 'valor', 'descricao', 'data'])
        for t in transacoes:
            writer.writerow([t.id, t.tipo, t.valor, t.descricao, t.data.strftime('%Y-%m-%d')])
        output.seek(0)
        return Response(output, mimetype='text/csv', headers={
            'Content-Disposition': 'attachment; filename=transacoes.csv'
        })
    else:
        return jsonify([
            {
                'id': t.id,
                'tipo': t.tipo,
                'valor': t.valor,
                'descricao': t.descricao,
                'data': t.data.strftime('%Y-%m-%d')
            } for t in transacoes
        ])

@finance_bp.route('/resumo', methods=['GET'])
@jwt_required()
def resumo_financeiro():
    user_id = get_jwt_identity()
    transacoes = Transaction.query.filter_by(user_id=user_id).all()
    saldo = sum(t.valor if t.tipo == 'receita' else -t.valor for t in transacoes)
    entradas = sum(t.valor for t in transacoes if t.tipo == 'receita')
    saidas = sum(t.valor for t in transacoes if t.tipo == 'despesa')
    return jsonify({
        'saldo': saldo,
        'entradas': entradas,
        'saidas': saidas
    })
