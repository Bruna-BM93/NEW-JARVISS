# Jarviss Backend - Checklist de Instalação e Execução

## 1. Instale as dependências
```bash
pip install -r requirements.txt
```

## Autenticação JWT

O backend utiliza autenticação JWT para proteger rotas sensíveis. Após o login, o usuário recebe um token JWT que deve ser enviado no header Authorization (Bearer) em todas as requisições protegidas.

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis (veja `.env.example`):

SECRET_KEY=...
JWT_SECRET_KEY=...
DATABASE_URL=...
WHATSAPP_TOKEN=...
WHATSAPP_PHONE_ID=...
OPENAI_API_KEY=...

## 3. Google Agenda
- Coloque o arquivo `credentials.json` (obtido no Google Cloud Console) na raiz do backend.
- Gere o token de acesso rodando:
```bash
python -c "from jarviss-backend.integrations.google_calendar import gerar_token_oauth2; gerar_token_oauth2()"
```

## 4. Inicialize o banco de dados
```bash
python jarviss-backend/db/init_db.py
```

## 5. Execute o servidor Flask
```bash
python jarviss-backend/app.py
```

## 6. Teste os endpoints
- Use ferramentas como Postman, Insomnia ou curl para testar os endpoints REST.

---

**Observações:**
- Certifique-se de rodar os comandos a partir da raiz do projeto.
- Para produção, configure variáveis de ambiente seguras e use um banco robusto (ex: PostgreSQL). 

## Planos e Limitações

- **Free:**
  - IA com limite de 3 perguntas/mês
  - IA com respostas genéricas
  - Painel financeiro básico
  - Histórico de 3 meses

- **Plus:**
  - IA com até 30 perguntas/mês
  - IA com dados reais
  - Gráficos, análise SWOT, DRE
  - Integração com notificações bancárias

- **Premium:**
  - IA com até 200 perguntas/mês (perguntas adicionais podem ser cobradas à parte)
  - Integração com WhatsApp/Instagram
  - Agenda Google + postagens automatizadas
  - Chatbot externo + CRM
  - Multiusuário

Se o limite do seu plano for atingido, será exibida uma mensagem de bloqueio ou sugestão de upgrade. No plano Premium, perguntas acima de 200/mês podem ser cobradas adicionalmente. 