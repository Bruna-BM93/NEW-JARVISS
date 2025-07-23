from flask import Blueprint, request, jsonify
try:
    from flask_jwt_extended import jwt_required
except ImportError:
    raise ImportError("O pacote 'flask_jwt_extended' não está instalado. Instale com 'pip install flask-jwt-extended'.")
from app import db
from models.produto import Produto
import logging

try:
    from marshmallow import Schema, fields, ValidationError
except ImportError:
    raise ImportError("O pacote 'marshmallow' não está instalado. Instale com 'pip install marshmallow'.")

produto_bp = Blueprint('produto', __name__)

def gerar_feedback_produto(produto):
    markup = (produto.preco_venda - produto.custo_compra) / produto.custo_compra * 100
    if markup < 20:
        return "Atenção: Markup baixo, reveja custos ou preço de venda."
    elif markup > 100:
        return "Ótimo markup! Considere investir mais neste produto."
    else:
        return "Markup saudável."

class ProdutoSchema(Schema):
    nome = fields.String(required=True)
    custo_compra = fields.Float(required=True)
    preco_venda = fields.Float(required=True)
    quantidade = fields.Integer()

@produto_bp.route('/produtos', methods=['POST'])
@jwt_required()
def cadastrar_produto():
    try:
        dados = request.get_json()
        schema = ProdutoSchema()
        try:
            validado = schema.load(dados)
        except ValidationError as err:
            return jsonify({'erro': 'Dados inválidos', 'detalhes': err.messages}), 400
        produto = Produto(**validado)
        db.session.add(produto)
        db.session.commit()
        return jsonify({'msg': 'Produto cadastrado com sucesso', 'id': produto.id}), 201
    except Exception as e:
        logging.exception('Erro ao cadastrar produto')
        return jsonify({'erro': 'Erro interno ao cadastrar produto', 'detalhe': str(e)}), 500

@produto_bp.route('/produtos', methods=['GET'])
@jwt_required()
def listar_produtos():
    try:
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
        except ValueError:
            page, per_page = 1, 10
        query = Produto.query.with_entities(
            Produto.id, Produto.nome, Produto.custo_compra, Produto.preco_venda, Produto.quantidade
        )
        # Corrigido: paginate não é método do Query do SQLAlchemy puro.
        # Usando limit/offset manual para paginação.
        total = query.count()
        produtos = query.offset((page - 1) * per_page).limit(per_page).all()
        def feedback(p):
            markup = (p.preco_venda - p.custo_compra) / p.custo_compra * 100
            if markup < 20:
                return "Atenção: Markup baixo, reveja custos ou preço de venda."
            elif markup > 100:
                return "Ótimo markup! Considere investir mais neste produto."
            else:
                return "Markup saudável."
        return jsonify([
            {
                'id': p.id,
                'nome': p.nome,
                'custo_compra': p.custo_compra,
                'preco_venda': p.preco_venda,
                'quantidade': p.quantidade,
                'markup': round((p.preco_venda - p.custo_compra) / p.custo_compra * 100, 2),
                'feedback': feedback(p)
            } for p in produtos
        ])
    except Exception as e:
        logging.exception('Erro ao listar produtos')
        return jsonify({'erro': 'Erro interno ao listar produtos', 'detalhe': str(e)}), 500 

def test_cadastrar_produto(client, access_token):
    resp = client.post('/produtos', json={
        'nome': 'Produto Teste',
        'custo_compra': 10,
        'preco_venda': 20
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert resp.status_code == 201