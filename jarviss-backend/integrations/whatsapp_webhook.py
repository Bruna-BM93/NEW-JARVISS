from flask import Blueprint, request, jsonify
from app import db
from models.lead_whatsapp import LeadWhatsapp
from datetime import datetime
import logging
import os
from integrations.media_handler import baixar_midia_whatsapp
import requests
from utils.validators import require_plano
from flask_jwt_extended import jwt_required

whatsapp_bp = Blueprint('whatsapp', __name__)

WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN')

# Configuração de logging local
logging.basicConfig(filename='whatsapp_webhook.log', level=logging.INFO, format='%(asctime)s %(message)s')

def enviar_mensagem_whatsapp(telefone, mensagem):
    """
    Envia mensagem de texto via WhatsApp Cloud API.
    """
    phone_id = os.environ.get('WHATSAPP_PHONE_ID')
    if not phone_id:
        logging.error('Variável de ambiente WHATSAPP_PHONE_ID não definida.')
        return {'error': 'WHATSAPP_PHONE_ID não definida'}
    url = f'https://graph.facebook.com/v17.0/{phone_id}/messages'
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'messaging_product': 'whatsapp',
        'to': telefone,
        'type': 'text',
        'text': {'body': mensagem}
    }
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code not in (200, 201):
        logging.error(f'Erro ao enviar mensagem WhatsApp: {resp.status_code} - {resp.text}')
    return resp.json()

@whatsapp_bp.route('/webhook/whatsapp', methods=['POST'])
@jwt_required()
@require_plano(['premium'])
def webhook_whatsapp():
    dados = request.get_json()
    logging.info(f'Recebido: {dados}')
    try:
        entry = dados.get('entry', [])[0]
        change = entry.get('changes', [])[0]
        value = change.get('value', {})
        messages = value.get('messages', [])
        if not messages:
            return jsonify({'status': 'no_message'}), 200
        msg = messages[0]
        telefone = msg.get('from')
        tipo_conteudo = msg.get('type')
        mensagem = ''
        arquivo_url = None
        nome = None
        # Buscar nome já cadastrado
        lead = LeadWhatsapp.query.filter_by(telefone=telefone).order_by(LeadWhatsapp.data_recebida.desc()).first()
        if tipo_conteudo == 'text':
            mensagem = msg['text']['body']
        elif tipo_conteudo == 'image':
            mensagem = msg['image'].get('caption', '')
            arquivo_url = msg['image'].get('url')
            if arquivo_url and WHATSAPP_TOKEN:
                try:
                    filename = f"{telefone}_{msg['id']}.jpg"
                    arquivo_url = baixar_midia_whatsapp(arquivo_url, WHATSAPP_TOKEN, filename)
                except Exception as e:
                    logging.error(f'Erro ao baixar imagem: {e}')
        elif tipo_conteudo == 'audio':
            mensagem = '[Áudio recebido]'
            arquivo_url = msg['audio'].get('url')
            if arquivo_url and WHATSAPP_TOKEN:
                try:
                    filename = f"{telefone}_{msg['id']}.ogg"
                    arquivo_url = baixar_midia_whatsapp(arquivo_url, WHATSAPP_TOKEN, filename)
                except Exception as e:
                    logging.error(f'Erro ao baixar áudio: {e}')
        # ... outros tipos podem ser tratados aqui
        # Fluxo automatizado
        if not lead or not lead.nome:
            # Primeira mensagem ou nome não cadastrado
            if tipo_conteudo == 'text' and all(x not in mensagem.lower() for x in ['meu nome', 'sou', 'chamo', 'nome']):
                resposta = 'Olá! Para te atender melhor, por favor, me diga seu nome completo 🙂'
                nome = None
            else:
                nome = mensagem.strip()
                resposta = f'Perfeito, {nome}! Agora, por favor, envie sua dúvida, orçamento ou arquivo que deseja analisar.'
        else:
            nome = lead.nome
            resposta = None  # Não precisa responder
        # Salvar lead
        novo_lead = LeadWhatsapp(
            nome=nome,
            telefone=telefone,
            mensagem=mensagem,
            tipo_conteudo=tipo_conteudo,
            arquivo_url=arquivo_url,
            data_recebida=datetime.utcnow(),
            origem='whatsapp',
            status='novo'
        )
        db.session.add(novo_lead)
        db.session.commit()
        # Enviar resposta automática (mock, implementar integração real depois)
        if resposta:
            logging.info(f'Resposta automática para {telefone}: {resposta}')
            enviar_mensagem_whatsapp(telefone, resposta)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logging.error(f'Erro no webhook: {e}')
        return jsonify({'status': 'error', 'detail': str(e)}), 500
