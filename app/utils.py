import datetime
import re
import html
import bcrypt
from flask import jsonify
from typing import Any, Dict

def sanitize_input(value: str) -> str:
    """Sanitiza qualquer string de entrada para prevenir ataques XSS e de injeção."""
    if not isinstance(value, str):
        return value
    # Escapa caracteres especiais HTML
    value = html.escape(value)
    # Remove quaisquer operadores MongoDB
    value = re.sub(r'\$[a-zA-Z]+', '', value)
    return value

def sanitize_email(email: str) -> str:
    """Sanitiza o email de entrada."""
    if not email:
        return ""
    # Converte para minúsculas
    email = email.lower().strip()
    # Remove quaisquer espaços em branco
    email = "".join(email.split())
    # Sanitização básica
    return sanitize_input(email)

def sanitize_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitiza recursivamente todos os valores string num documento."""
    if not isinstance(doc, dict):
        return doc
    
    sanitized = {}
    for key, value in doc.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_document(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_document(item) if isinstance(item, dict) 
                            else sanitize_input(item) if isinstance(item, str)
                            else item for item in value]
        else:
            sanitized[key] = value
    return sanitized

def hash_password(password: str) -> str:
    """Encripta a palavra-passe utilizando bcrypt."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verifica a palavra-passe contra o hash."""
    if isinstance(password, bytes):
        pwd = password
    else:
        pwd = password.encode('utf-8')
        
    if isinstance(hashed, bytes):
        hashed_pwd = hashed
    else:
        hashed_pwd = hashed.encode('utf-8')
        
    return bcrypt.checkpw(pwd, hashed_pwd)

# Função para padronizar as respostas da API
# Parâmetros:
#   data: dados a serem retornados na resposta
#   message: mensagem descritiva do resultado da operação
#   code: código HTTP da resposta (200=sucesso, 201=criado, 4xx=erro cliente, 5xx=erro servidor)
def response(data, message, code):
    # Define o status de sucesso baseado no código HTTP
    code_text = "true"
    dt = datetime.datetime.now()
    if code != 200 and code != 201 and code != 203:
        code_text = "false"
    
    # Monta o objeto de resposta padronizado
    text = {
        "success": code_text,      # Indica se a operação foi bem sucedida
        "code": code,              # Código HTTP da resposta
        "message": message,        # Mensagem descritiva
        "data": data,             # Dados da resposta
        "date": datetime.datetime.timestamp(dt),  # Timestamp da resposta
    }
    return jsonify(text), code  # Retorna o JSON formatado com o código HTTP
