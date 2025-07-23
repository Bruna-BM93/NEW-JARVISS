from flask_jwt_extended import jwt_required, get_jwt_identity
from models.transaction import Transaction
from app import db
from flask import request, jsonify
from integrations.google_calendar import agendar_evento
import datetime
from services.ia_service import resposta_multi_agente
from models.user import User
from models.notification import Notification
from utils.validators import require_plano
from models.resposta_ia import RespostaIA
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

def verificar_permissao_ia(usuario, comando):
    comandos_liberados_free = [
        "Qual foi meu lucro no mês passado?",
        "O que são despesas fixas?",
        "Como posso organizar minhas finanças?"
    ]
    comandos_premium_only = [
        "criar_post_ia", "integracao_whatsapp", "agendamento_google"
    ]
    if usuario.plano == 'free':
        # Exemplo: limite de 3 perguntas por semana
        if False:  # Implemente a lógica de limite
            return "Você usou o limite semanal de perguntas com IA no plano gratuito. Atualize para o plano Plus para liberar respostas ilimitadas."
        if comando in comandos_liberados_free:
            return "OK"
        else:
            return "upgrade:plus"
    elif usuario.plano == 'plus':
        if comando in comandos_premium_only:
            return "upgrade:premium"
        return "OK"
    return "OK"

def notificar_upgrade(usuario_id, sugestao, plano_recomendado):
    notificacao = Notification(
        usuario_id=usuario_id,
        mensagem=sugestao,
        plano_recomendado=plano_recomendado,
        status="pendente"
    )
    db.session.add(notificacao)
    db.session.commit()

@ai_bp.route('/ia/pergunta', methods=['POST'])
@jwt_required()
def ia_pergunta():
    dados = request.get_json()
    pergunta = dados.get('pergunta')
    user_id = get_jwt_identity()
    if not pergunta:
        return jsonify({'msg': 'Pergunta é obrigatória'}), 400
    # Simulação: se perguntar saldo, responde com saldo real
    if 'saldo' in pergunta.lower():
        transacoes = Transaction.query.filter_by(user_id=user_id).all()
        saldo = sum(t.valor if t.tipo == 'receita' else -t.valor for t in transacoes)
        resposta = f'Seu saldo atual é R$ {saldo:.2f}.'
    else:
        resposta = 'Esta é uma resposta simulada da IA. Em breve, integração real com OpenAI.'
    return jsonify({'resposta': resposta})

@ai_bp.route('/agendar_evento', methods=['POST'])
@jwt_required()
@require_plano(['premium'])
def agendar_evento_route():
    dados = request.get_json()
    try:
        titulo = dados['titulo']
        descricao = dados.get('descricao', '')
        data_inicio = datetime.datetime.fromisoformat(dados['data_inicio'])
        data_fim = datetime.datetime.fromisoformat(dados['data_fim'])
        email_usuario = dados['email_usuario']
        evento_id = agendar_evento(titulo, descricao, data_inicio, data_fim, email_usuario)
        return jsonify({'status': 'ok', 'evento_id': evento_id}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'detail': str(e)}), 400

@ai_bp.route('/pergunta_ia', methods=['POST'])
@jwt_required()
@require_plano(['free', 'plus', 'premium'])
def pergunta_ia():
    user_id = get_jwt_identity()
    usuario = User.query.get(user_id)
    comando = request.json.get('comando')
    permissao = verificar_permissao_ia(usuario, comando)
    if permissao == "OK":
        # Limite de chamadas por mês
        agora = datetime.utcnow()
        inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total_chamadas = RespostaIA.query.filter(
            RespostaIA.user_id == user_id,
            RespostaIA.data >= inicio_mes
        ).count()
        limites = {'free': 3, 'plus': 30, 'premium': 200}
        limite = limites.get(usuario.plano, 3)
        if usuario.plano != 'premium' and total_chamadas >= limite:
            return jsonify({'erro': f'Limite de {limite} perguntas/mês atingido para seu plano. Faça upgrade para liberar mais.'}), 403
        if usuario.plano == 'premium' and total_chamadas >= limite:
            # Premium pode ser notificado sobre cobrança adicional
            return jsonify({'erro': 'Você atingiu o limite de 200 perguntas/mês. Perguntas adicionais podem ser cobradas à parte.'}), 403
        resposta = resposta_multi_agente(comando, {}, usuario.plano)
        if hasattr(resposta, 'content'):
            resposta = resposta.content
        resposta = resposta.strip('```json').strip('```').strip()
        # Registrar uso
        registro = RespostaIA(user_id=user_id, plano=usuario.plano, pergunta=comando, resposta=resposta)
        db.session.add(registro)
        db.session.commit()
        return jsonify({"resposta": resposta})
    elif permissao.startswith("upgrade"):
        plano = permissao.split(":")[1]
        sugestao = f"Esse recurso está disponível no plano {plano.capitalize()}. Atualize para liberar!"
        notificar_upgrade(usuario.id, sugestao, plano)
        return jsonify({"erro": "Recurso não disponível no seu plano", "sugestao": sugestao}), 403
    else:
        return jsonify({"erro": permissao}), 403
