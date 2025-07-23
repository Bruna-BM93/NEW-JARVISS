from flask import Blueprint, request, jsonify
import requests
try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

try:
    from flask_jwt_extended import jwt_required
except ImportError:
    def jwt_required():
        def decorator(fn):
            return fn
        return decorator
from functools import lru_cache
import time
import logging

integrations_bp = Blueprint('integrations', __name__)

@integrations_bp.route('/integracao/cnpj/<cnpj>', methods=['GET'])
@jwt_required()
def cnpj_publica(cnpj):
    try:
        url = f"https://publica.cnpj.ws/cnpj/{cnpj}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        logging.exception('Erro ao consultar CNPJ')
        return jsonify({'erro': 'Falha ao consultar CNPJ', 'detalhe': str(e)}), 503

@integrations_bp.route('/integracao/cep/<cep>', methods=['GET'])
@jwt_required()
def via_cep(cep):
    try:
        url = f"https://viacep.com.br/ws/{cep}/json/"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        logging.exception('Erro ao consultar CEP')
        return jsonify({'erro': 'Falha ao consultar CEP', 'detalhe': str(e)}), 503

@integrations_bp.route('/integracao/ibge/cidades/<uf>', methods=['GET'])
@jwt_required()
def ibge_cidades(uf):
    try:
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        cidades = [c['nome'] for c in resp.json()] if resp.status_code == 200 else []
        return jsonify(cidades), resp.status_code
    except Exception as e:
        logging.exception('Erro ao consultar cidades IBGE')
        return jsonify({'erro': 'Falha ao consultar cidades IBGE', 'detalhe': str(e)}), 503

@lru_cache(maxsize=32)
def bacen_selic_cache():
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/1?formato=json"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()[0]['valor'], time.time()
    except Exception as e:
        logging.exception('Erro ao consultar BACEN SELIC')
        return None, time.time()

@integrations_bp.route('/integracao/bacen/selic', methods=['GET'])
@jwt_required()
def bacen_selic():
    valor, ts = bacen_selic_cache()
    cache_age = int(time.time() - ts)
    if valor:
        return jsonify({'selic': valor, 'cache_age_seconds': cache_age}), 200
    return jsonify({'erro': 'Não encontrado'}), 404

@integrations_bp.route('/integracao/brasilio/municipios', methods=['GET'])
@jwt_required()
def brasilio_municipios():
    try:
        token = request.headers.get('Authorization', '').replace('Token ', '')
        url = "https://api.brasil.io/v1/dataset/covid19/caso/data/"
        headers = {"Authorization": f"Token {token}"}
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        logging.exception('Erro ao consultar Brasil.IO')
        return jsonify({'erro': 'Falha ao consultar Brasil.IO', 'detalhe': str(e)}), 503

@lru_cache(maxsize=32)
def trends_cache(termo, geo):
    try:
        if TrendReq is None:
            raise ImportError("pytrends não está instalado")
        pytrends = TrendReq()
        pytrends.build_payload([termo], cat=0, timeframe='now 7-d', geo=geo)
        return pytrends.interest_over_time().to_dict(), time.time()
    except Exception as e:
        logging.exception('Erro ao consultar Google Trends')
        return {}, time.time()
            return {}, time.time()

@integrations_bp.route('/integracao/trends', methods=['GET'])
@jwt_required()
def google_trends():
    try:
        termo = request.args.get('termo', 'negócios')
        geo = request.args.get('geo', 'BR')
        data, ts = trends_cache(termo, geo)
        cache_age = int(time.time() - ts)
        return jsonify({'data': data, 'cache_age_seconds': cache_age})
    except Exception as e:
        logging.exception('Erro ao consultar Google Trends')
        return jsonify({'erro': 'Falha ao consultar Google Trends', 'detalhe': str(e)}), 503 