import os
import requests
from datetime import datetime
from models.transaction import Transaction
from sqlalchemy import func

def gerar_swot(dados_empresa):
    # Exemplo simplificado
    return {
        "forcas": ["Marca reconhecida", "Equipe qualificada"],
        "fraquezas": ["Baixo capital de giro"],
        "oportunidades": ["Mercado em expansão em Blumenau"],
        "ameacas": ["Concorrência local forte"]
    }

def swot_from_db(user_id, db):
    # Forças: maiores receitas
    forcas = db.session.query(Transaction.descricao, func.sum(Transaction.valor))\
        .filter(Transaction.tipo == 'receita', Transaction.user_id == user_id)\
        .group_by(Transaction.descricao)\
        .order_by(func.sum(Transaction.valor).desc())\
        .limit(3).all()
    forcas = [f"{desc} (R$ {valor:.2f})" for desc, valor in forcas]

    # Fraquezas: maiores despesas
    fraquezas = db.session.query(Transaction.descricao, func.sum(Transaction.valor))\
        .filter(Transaction.tipo == 'despesa', Transaction.user_id == user_id)\
        .group_by(Transaction.descricao)\
        .order_by(func.sum(Transaction.valor).desc())\
        .limit(3).all()
    fraquezas = [f"{desc} (R$ {valor:.2f})" for desc, valor in fraquezas]

    # Oportunidades: crescimento de receita mês a mês
    oportunidades = db.session.query(
        func.strftime('%Y-%m', Transaction.data), func.sum(Transaction.valor)
    ).filter(Transaction.tipo == 'receita', Transaction.user_id == user_id)\
     .group_by(func.strftime('%Y-%m', Transaction.data))\
     .order_by(func.sum(Transaction.valor).desc())\
     .limit(3).all()
    oportunidades = [f"Mês {mes}: R$ {valor:.2f}" for mes, valor in oportunidades]

    # Ameaças: meses com maiores despesas
    ameacas = db.session.query(
        func.strftime('%Y-%m', Transaction.data), func.sum(Transaction.valor)
    ).filter(Transaction.tipo == 'despesa', Transaction.user_id == user_id)\
     .group_by(func.strftime('%Y-%m', Transaction.data))\
     .order_by(func.sum(Transaction.valor).desc())\
     .limit(3).all()
    ameacas = [f"Mês {mes}: R$ {valor:.2f}" for mes, valor in ameacas]

    return {
        "forcas": forcas,
        "fraquezas": fraquezas,
        "oportunidades": oportunidades,
        "ameacas": ameacas
    }

def chatgpt_responder(contexto):
    try:
        api_key = os.environ.get('API_CHATGPT')
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Responda como um empresário de Blumenau/SC, simpático e analista."},
                {"role": "user", "content": contexto}
            ]
        }
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except (KeyError, IndexError):
        return "[ChatGPT] Erro: resposta inesperada da API."
    except Exception as e:
        return f"[ChatGPT] Erro: {str(e)}"

def gemini_responder(contexto):
    try:
        api_key = os.environ.get('API_GEMINI')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        data = {
            "contents": [{"parts": [{"text": contexto}]}]
        }
        resp = requests.post(url, json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError):
        return "[Gemini] Erro: resposta inesperada da API."
    except Exception as e:
        return f"[Gemini] Erro: {str(e)}"

def grok_responder(contexto):
    try:
        api_key = os.environ.get('API_GROK')
        url = "https://api.grok.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "grok-1",
            "messages": [
                {"role": "system", "content": "Responda como um empresário de Blumenau/SC, simpático e analista."},
                {"role": "user", "content": contexto}
            ]
        }
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content']
    except (KeyError, IndexError):
        return "[Grok] Erro: resposta inesperada da API."
    except Exception as e:
        return f"[Grok] Erro: {str(e)}"

def escolher_resposta(respostas):
    # Exemplo: prioriza ChatGPT, depois Gemini, depois Grok
    return respostas[0] if respostas else "Sem resposta."

def resposta_multi_agente(pergunta, dados_empresa, plano_ativo):
    swot = gerar_swot(dados_empresa)
    contexto = f"Empresa de Blumenau/SC. SWOT: {swot}. Pergunta: {pergunta}"
    respostas = [
        chatgpt_responder(contexto),
        gemini_responder(contexto),
        grok_responder(contexto)
    ]
    return escolher_resposta(respostas)

def prompt_humanizado(pergunta, swot, tendencias, perfil_empresa):
    return (
        f"Olá! Sou seu Consultor Empresarial.\n"
        f"Perfil: {perfil_empresa}.\n"
        f"Aqui está uma análise SWOT da sua empresa: {swot}.\n"
        f"Tendências do seu segmento: {tendencias}.\n"
        f"Sua dúvida: {pergunta}\n"
        f"Sugestões práticas, ideias para engajar clientes e insights de mercado virão a seguir.\n"
    )

def buscar_tendencias_mercado(nicho):
    # Exemplo mock: em produção, integre com Google Trends, IBGE, etc.
    return f"Produtos mais buscados em {nicho}: Software de gestão, automação financeira, consultoria digital. Concorrentes: Empresa X, Empresa Y. Ideias: Programa de fidelidade, eventos online, marketing de conteúdo."
