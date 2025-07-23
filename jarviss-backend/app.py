from flask import Flask
from flask_cors import CORS

try:
    from flask_jwt_extended import JWTManager
except ImportError:
    JWTManager = None

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    SQLAlchemy = None
except ImportError:
    SQLAlchemy = None
try:
    from flask_restx import Api
except ImportError:
    Api = None
from config import Config
import os
from flask_migrate import Migrate

# Inicializações globais
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app, doc='/docs', title='Jarviss API', description='API do Assistente Empresarial Digital')

# Importar e registrar blueprints
from routes.auth import auth_bp
from routes.finance import finance_bp
from routes.ai import ai_bp
from routes.budget import budget_bp
from integrations.whatsapp_webhook import whatsapp_bp
from routes.swot import swot_bp
from routes.integrations import integrations_bp
from routes.produto import produto_bp
from routes.cliente import cliente_bp
from routes.fornecedor import fornecedor_bp

app.register_blueprint(auth_bp)
app.register_blueprint(finance_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(budget_bp)
app.register_blueprint(whatsapp_bp)
app.register_blueprint(swot_bp)
app.register_blueprint(integrations_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(fornecedor_bp)

if __name__ == '__main__':
    app.run(debug=True)
