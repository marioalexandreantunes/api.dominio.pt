# Importações do sistema
import os
import datetime

from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from .swagger import template

# Importações do Flask e suas extensões
from flask import Flask, request
from flask_limiter import Limiter  # Para controle de taxa de requisições
from flask_limiter.util import get_remote_address

__all__ = ['api']
from dotenv import load_dotenv  # Para carregar variáveis de ambiente
from flask_sslify import SSLify # Para forçar HTTPS em produção
from flask_jwt_extended import JWTManager  # Para autenticação JWT

from werkzeug.serving import WSGIRequestHandler

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv(override=True)

# Função para verificar modo debug
DEBUG = bool(os.getenv("DEBUG") == "true")

# Inicialização da aplicação Flask
api = Flask(__name__)
api.config.update(
    DEBUG=DEBUG,
    ENV='development' if DEBUG else 'production',
    TESTING=False
)

# Log do modo atual
print(f"Modo Debug: {'ATIVADO' if DEBUG else 'DESATIVADO'}")
CORS(api, resources={r"/api/*": {"origins": "*"}})

# Configuração para remover o cabeçalho Server
WSGIRequestHandler.server_version = ""
WSGIRequestHandler.sys_version = ""

class CustomRequestHandler(WSGIRequestHandler):
    def version_string(self):
        return ''

api.config['SERVER_NAME'] = None

# Configuração do formato JSON
api.json.sort_keys = False  # Mantém a ordem das chaves no JSON

# Configurações de Segurança
# Em produção, força todas as requisições a usarem HTTPS
if(not DEBUG):
    sslify = SSLify(api)
    
# Configuração do JWT para autenticação
jwt = JWTManager(api)
api.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")  # Chave secreta para tokens
api.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=7)  # Tempo de expiração do token

# Middleware para adicionar cabeçalhos de segurança
@api.after_request
def add_security_headers(response):
    # Strict Transport Security: força HTTPS por 1 ano
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content Security Policy: restringe origens de conteúdo
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;"
    
    # X-Frame-Options: previne clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # X-Content-Type-Options: previne MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Referrer-Policy: controla informações do referrer
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions-Policy: restringe funcionalidades do navegador
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

# Configuração do limitador de requisições
# Previne abusos limitando o número de requisições por IP
limiter = Limiter(
    key_func=get_remote_address,  # Usa o IP como identificador
    storage_uri="memory://",  # Armazena contadores na memória (outras opções: redis://, memcached://, etc. para persistência e escalabilidade)
    application_limits=["1 per second"]  # Limite padrão de 2 requisições por minuto
)

# Aplica o limitador à aplicação
limiter.init_app(api)

# Configura exceção para rotas do Swagger UI
@limiter.request_filter
def limiter_filter():
    return request.path.startswith('/api/docs')

# Importação das rotas após inicialização do limitador
# Importante: evita problemas de importação circular
from app.routes import api_bp  # noqa: E402

# Registro do Blueprint da API
# Todas as rotas terão o prefixo /api/v1
api.register_blueprint(api_bp, url_prefix='/api/v1')

# Configuração do Swagger UI
SWAGGER_URL = '/api/docs'
swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    None,
    config={
        'app_name': "API Mario Code Labs",
        'spec': template
    }
)
api.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)
