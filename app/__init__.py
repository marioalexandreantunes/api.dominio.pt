# Importações do sistema
import os
import datetime
from typing import Dict, Any

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

def validate_env_variables() -> Dict[str, Any]:
    """
    Valida todas as variáveis de ambiente necessárias.
    Retorna um dicionário com as variáveis validadas.
    Lança exceção se alguma validação falhar.
    """
    # Carrega as variáveis de ambiente
    load_dotenv(override=True)
    
    # Define as variáveis obrigatórias e seus tipos esperados
    required_vars = {
        'DATABASE_URL': {
            'type': str,
            'validator': lambda x: x.startswith('mongodb'),
            'error': 'DATABASE_URL deve ser uma URL MongoDB válida'
        },
        'JWT_SECRET_KEY': {
            'type': str,
            'validator': lambda x: len(x) >= 32,
            'error': 'JWT_SECRET_KEY deve ter pelo menos 32 caracteres'
        },
        'TOKEN_HEADER_KEY': {
            'type': str,
            'validator': lambda x: len(x) > 0,
            'error': 'TOKEN_HEADER_KEY não pode estar vazio'
        },
        'PORT_DEBUG': {
            'type': int,
            'validator': lambda x: 1024 <= x <= 65535,
            'error': 'PORT_DEBUG deve estar entre 1024 e 65535'
        },
        'DEBUG': {
            'type': str,
            'validator': lambda x: x.lower() in ['true', 'false'],
            'error': 'DEBUG deve ser "true" ou "false"'
        }
    }
    
    validated_vars = {}
    
    for var_name, config in required_vars.items():
        # Verifica se a variável existe
        value = os.getenv(var_name)
        if value is None:
            raise ValueError(f'Variável de ambiente {var_name} não encontrada')
            
        # Converte para o tipo correto
        try:
            if config['type'] is int:
                value = int(value)
            elif config['type'] is bool and isinstance(value, str):
                value = value.lower() == 'true'
        except ValueError:
            raise ValueError(f'Variável {var_name} tem tipo inválido. Esperado: {config["type"].__name__}')
            
        # Aplica validação específica
        if not config['validator'](value):
            raise ValueError(config['error'])
            
        validated_vars[var_name] = value
    
    return validated_vars

# Valida as variáveis de ambiente antes de iniciar a aplicação
try:
    env_vars = validate_env_variables()
    DEBUG = env_vars['DEBUG'].lower() == 'true'
except Exception as e:
    print(f"Erro na validação das variáveis de ambiente: {str(e)}")
    raise SystemExit(1)

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
api.config["JWT_SECRET_KEY"] = env_vars["JWT_SECRET_KEY"]  # Chave secreta para tokens
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
    storage_uri="memory://",  # Armazena contadores na memória
    default_limits=["100 per day", "30 per hour", "5 per minute"],  # Limites padrão globais
    strategy="fixed-window-elastic-expiry",  # Estratégia mais robusta para contagem
    headers_enabled=True,  # Habilita headers de rate limit na resposta
    swallow_errors=True,  # Continua funcionando mesmo se houver erros no storage
    retry_after="http-date"  # Formato do header Retry-After
)

# Aplica o limitador à aplicação
limiter.init_app(api)

# Configura exceções para rotas específicas
@limiter.request_filter
def limiter_filter():
    # Ignora rate limiting para documentação e health checks
    return request.path.startswith('/api/docs') or \
           request.path.startswith('/api/v1/health')

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
