# Importações necessárias
import logging  # Para registro de logs
import os      # Para variáveis de ambiente
import datetime # Para manipulação de datas

# Importações do Flask e extensões
from flask import Blueprint, request
from app.validators import validate_request
from app.utils import (
    response, 
    sanitize_document, 
    sanitize_email, 
    hash_password,
    verify_password,
    is_ip_blocked,
    record_failed_attempt,
    clear_failed_attempts
)
from app import limiter

# Importações do MongoDB
from pymongo.mongo_client import MongoClient

# Importações para autenticação JWT
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
)

# Criação do Blueprint da API
api_bp = Blueprint('api', __name__)

# Configuração da conexão com o MongoDB
uri = os.getenv("DATABASE_URL")
#client = MongoClient(uri, server_api=ServerApi("1"))
client = MongoClient(
    uri,
    maxPoolSize=50,
    waitQueueTimeoutMS=2500,
    serverSelectionTimeoutMS=5000
)
db = client["Cluster0"]
users_collection = db["User"]


# Rotas
# Rota para verificar o status da API e conexão com o banco de dados
@api_bp.route("/", methods=["GET"])
@limiter.limit("10 per minute")  # Limite de 10 requisições por minuto para status check
def status():
    logging.info("route '/' status()")
    try:
        one = users_collection.count_documents({})
        return response(one, "Status OK", 200)
    except Exception as err:
        return response(err, "Status OFF", 500)
    

# Rota para criar o primeiro usuário administrador (superuser)
# Só pode ser usado uma vez quando não existem usuários no sistema
@api_bp.route("/createsuperuser", methods=["POST"])
@limiter.limit("3 per day")  # Limite mais restrito para criação de superusuário
@validate_request('registration')
def createsuperuser():
    logging.info("route '/createsuperuser' createsuperuser()")
    new_user = request.get_json()  # Armazena o corpo da requisição JSON
    try:
        one = users_collection.count_documents({})
        print("Quantos existem?", one)
        if one == 0:
            # Sanitização da entrada
            new_user = sanitize_document(new_user)
            new_user["email"] = sanitize_email(new_user["email"])
            # Hash da palavra-passe
            new_user["password"] = hash_password(new_user["password"])
            users_collection.insert_one(new_user)
            print(new_user)
            del new_user["_id"]
            return response(new_user, "Utilizador criado com sucesso", 201)
        else:
            return response(new_user, "Já existem utilizadores", 409)
    except Exception as err:
        return response(err, "Nome de utilizador já existe", 409)

# Rota para autenticação de utilizadores
# Retorna um token JWT válido por 7 minutos se as credenciais estiverem corretas
@api_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute, 20 per hour")  # Limite rigoroso para tentativas de login
@validate_request('login')
def login():
    logging.info("route '/login' login()")
    
    # Verifica se o IP está bloqueado
    ip = request.remote_addr
    is_blocked, remaining_time = is_ip_blocked(ip)
    if is_blocked:
        return response(
            {"blocked_for": remaining_time},
            f"Demasiadas tentativas falhadas. Tente novamente em {remaining_time} segundos",
            429
        )
    
    login_details = request.get_json()
    # Sanitização da entrada
    login_details = sanitize_document(login_details)
    email = sanitize_email(login_details["email"])
    
    user_from_db = users_collection.find_one({"email": email})
    if user_from_db:
        if verify_password(login_details["password"], user_from_db["password"]):
            # Limpa as tentativas falhadas após login bem-sucedido
            clear_failed_attempts(ip)
            access_token = create_access_token(
                identity=user_from_db["email"],
                expires_delta=datetime.timedelta(minutes=7),
            )
            return response(
                {"access_token": access_token}, "Login realizado com sucesso", 200
            )
    
    # Regista a tentativa falhada
    record_failed_attempt(ip)
    return response(login_details, "Email ou palavra-passe incorretos", 401)

# Rota para cadastrar novos utilizadores
# Requer autenticação JWT (token válido)
@api_bp.route("/cadastro", methods=["POST"])
@jwt_required()
@limiter.limit("20 per hour")  # Limite para criação de novos usuários
@validate_request('registration')
def cadastro():
    logging.info("route '/cadastro' cadastro()")
    new_user = request.get_json()  # Armazena o corpo da requisição JSON
    # Sanitização da entrada
    new_user = sanitize_document(new_user)
    new_user["email"] = sanitize_email(new_user["email"])
    # Hash da palavra-passe
    new_user["password"] = hash_password(new_user["password"])
    
    doc = users_collection.find_one({"email": new_user["email"]})  # Verifica se o utilizador existe
    if not doc:
        users_collection.insert_one(new_user)
        del new_user["_id"]
        return response(new_user, "Utilizador criado com sucesso", 201)
    else:
        return response(new_user["email"], "Email já existe", 409)
    
    
# Rota para listar todos os utilizadores cadastrados
# Requer autenticação JWT (token válido)
# Remove informações sensíveis (palavra-passe e ID) antes de retornar
@api_bp.route("/cadastros", methods=["GET"])
@jwt_required()
@limiter.limit("30 per minute")  # Limite para listagem de usuários
def cadastros():
    logging.info("route '/cadastros' cadastros()")
    user_from_db = users_collection.find()
    myList = []
    if user_from_db:
        for user in user_from_db:
            del user["_id"], user["password"]
            myList.append(user)
        return response(myList, "Utilizadores obtidos com sucesso", 200)
    else:
        return response(user_from_db, "Utilizadores não encontrados", 404)
    

# Tratamento de erro para limite de requisições
@api_bp.errorhandler(429)
def ratelimit_handler(e):
    logging.info("ratelimit_handler()" + str(e))
    retry_after = e.description.split('in')[1].strip() if 'in' in e.description else '60 seconds'
    return response(
        {
            "error": "rate_limit_exceeded",
            "retry_after": retry_after,
            "message": str(e)
        },
        "Demasiadas Requisições. Por favor, tente novamente mais tarde.",
        429
    )

# Tratamento de erro para rotas não encontradas (404)
@api_bp.errorhandler(404)
def not_found_error(error):
    logging.info("not_found_error()" + str(error))
    return response(str(error).replace(":", "-"), "Não Encontrado", 404)


# Tratamento de erro para erros internos do servidor (500)
@api_bp.errorhandler(500)
def internal_error(error):
    logging.info("internal_error()" + str(error))
    return response(str(error).replace(":", "-"), "Erro Interno do Servidor", 500)
