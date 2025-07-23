import requests
import os

def baixar_midia_whatsapp(media_url, token, filename, pasta_destino='media'):
    """
    Baixa arquivo de mídia do WhatsApp Cloud API e salva localmente.
    Retorna o caminho do arquivo salvo.
    """
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    headers = {
        'Authorization': f'Bearer {token}'
    }
    resposta = requests.get(media_url, headers=headers, stream=True)
    if resposta.status_code == 200:
        caminho_arquivo = os.path.join(pasta_destino, filename)
        with open(caminho_arquivo, 'wb') as f:
            for chunk in resposta.iter_content(1024):
                f.write(chunk)
        return caminho_arquivo
    else:
        raise Exception(f'Erro ao baixar mídia: {resposta.status_code} - {resposta.text}')
