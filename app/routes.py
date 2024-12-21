# Importações necessárias
import logging  # Para registro de logs
import os      # Para variáveis de ambiente
import hashlib # Para criptografia de senhas
import datetime # Para manipulação de datas

# Importações do Flask e extensões
from flask import Blueprint, request
from app.validators import validate_request
from app.utils import response
from app import limiter

# Importações do MongoDB
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Importações para autenticação JWT
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
)

# Criação do Blueprint da API
api_bp = Blueprint('api', __name__)

# Configuração da conexão com o MongoDB
uri = os.getenv("DATABASE_URL")
client = MongoClient(uri, server_api=ServerApi("1"))
db = client["Cluster0"]
users_collection = db["User"]


# rotas
# Rota para verificar o status da API e conexão com o banco de dados
@api_bp.route("/", methods=["GET"])
@limiter.limit("1 per minute")  # Limite de 1 requisição por minuto
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
@limiter.limit("2 per hour")  # Limite de 1 requisição por hora
@validate_request('registration')
def createsuperuser():
    logging.info("route '/createsuperuser' createsuperuser()")
    new_user = request.get_json()  # store the json body request
    try:
        one = users_collection.count_documents({})
        print("How many exist?", one)
        if one == 0:
            new_user["password"] = hashlib.sha256(
                new_user["password"].encode("utf-8")
            ).hexdigest()  # encrpt password
            users_collection.insert_one(new_user)
            print(new_user)
            del new_user["_id"]
            return response(new_user, "User created successfully", 201)
        else:
            return response(new_user, "Users already exists", 409)
    except Exception as err:
        return response(err, "Username already exists", 409)

# Rota para autenticação de usuários
# Retorna um token JWT válido por 7 minutos se as credenciais estiverem corretas
@api_bp.route("/login", methods=["POST"])
@validate_request('login')
def login():
    logging.info("route '/login' login()")
    login_details = request.get_json()
    user_from_db = users_collection.find_one({"email": login_details["email"]})
    if user_from_db:
        encrpted_password = hashlib.sha256(
            login_details["password"].encode("utf-8")
        ).hexdigest()
        if encrpted_password == user_from_db["password"]:
            access_token = create_access_token(
                identity=user_from_db["email"],
                expires_delta=datetime.timedelta(minutes=7),
            )
            return response(
                {"access_token": access_token}, "User login successfully", 200
            )
    return response(login_details, "The email or password is incorrect", 401)

# Rota para cadastrar novos usuários
# Requer autenticação JWT (token válido)
@api_bp.route("/cadastro", methods=["POST"])
@jwt_required()
@validate_request('registration')
def cadastro():
    logging.info("route '/cadastro' cadastro()")
    new_user = request.get_json()  # store the json body request
    new_user["password"] = hashlib.sha256(
        new_user["password"].encode("utf-8")
    ).hexdigest()  # encrpt password
    doc = users_collection.find_one({"email": new_user["email"]})  # check if user exist
    if not doc:
        users_collection.insert_one(new_user)
        del new_user["_id"]
        return response(new_user, "User created successfully", 201)
    else:
        return response(new_user["email"], "User email already exists", 409)
    
    
# Rota para listar todos os usuários cadastrados
# Requer autenticação JWT (token válido)
# Remove informações sensíveis (senha e ID) antes de retornar
@api_bp.route("/cadastros", methods=["GET"])
@jwt_required()
def cadastros():
    logging.info("route '/cadastros' cadastros()")
    user_from_db = users_collection.find()
    myList = []
    if user_from_db:
        for user in user_from_db:
            del user["_id"], user["password"]
            myList.append(user)
        return response(myList, "Get Users successfully", 200)
    else:
        return response(user_from_db, "Users not found", 404)
    

# Tratamento de erro para rotas não encontradas (404)
@api_bp.errorhandler(404)
def not_found_error(error):
    logging.info("not_found_error()" + str(error))
    return response(str(error).replace(":", "-"), "Not Found", 404)


# Tratamento de erro para erros internos do servidor (500)
@api_bp.errorhandler(500)
def internal_error(error):
    logging.info("internal_error()" + str(error))
    return response(str(error).replace(":", "-"), "Internal Server Error", 500)
