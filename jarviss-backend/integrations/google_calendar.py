from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import os
from google_auth_oauthlib.flow import InstalledAppFlow

def agendar_evento(titulo, descricao, data_inicio, data_fim, email_usuario, token_path='token.json', cred_path='credentials.json'):
    """
    Cria um evento no Google Agenda do usuário autenticado.
    Retorna o ID do evento criado.
    """
    # Carregar credenciais
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar'])
    else:
        raise Exception('Token de autenticação Google não encontrado. Faça o fluxo OAuth2.')
    service = build('calendar', 'v3', credentials=creds)
    evento = {
        'summary': titulo,
        'description': descricao,
        'start': {
            'dateTime': data_inicio.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'end': {
            'dateTime': data_fim.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'attendees': [
            {'email': email_usuario},
        ],
    }
    evento_criado = service.events().insert(calendarId='primary', body=evento, sendUpdates='all').execute()
    return evento_criado.get('id')

def gerar_token_oauth2(cred_path='credentials.json', token_path='token.json'):
    """
    Inicia o fluxo OAuth2 e salva o token.json para o Google Agenda.
    """
    flow = InstalledAppFlow.from_client_secrets_file(cred_path, scopes=['https://www.googleapis.com/auth/calendar'])
    creds = flow.run_local_server(port=0)
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
    return token_path
