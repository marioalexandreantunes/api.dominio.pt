import datetime
import re
import html
import bcrypt
from flask import jsonify
from typing import Any, Dict
from collections import defaultdict
import time

# Rastreia tentativas de login falhadas
failed_attempts = defaultdict(list)
BLOCK_TIME = 900  # 15 minutos em segundos
MAX_ATTEMPTS = 5  # Número máximo de tentativas antes do bloqueio

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

def is_ip_blocked(ip: str) -> tuple[bool, int]:
    """
    Verifica se um IP está bloqueado e por quanto tempo.
    Retorna (está_bloqueado, tempo_restante_em_segundos)
    """
    if ip not in failed_attempts:
        return False, 0
    
    attempts = failed_attempts[ip]
    if len(attempts) < MAX_ATTEMPTS:
        return False, 0
    
    # Clean up old attempts
    current_time = time.time()
    attempts = [t for t in attempts if current_time - t < BLOCK_TIME]
    failed_attempts[ip] = attempts
    
    if len(attempts) >= MAX_ATTEMPTS:
        newest_attempt = max(attempts)
        block_remaining = int(BLOCK_TIME - (current_time - newest_attempt))
        return True, max(0, block_remaining)
    
    return False, 0

def record_failed_attempt(ip: str):
    """Regista uma tentativa de login falhada para um IP"""
    current_time = time.time()
    # Clean up old attempts
    attempts = failed_attempts.get(ip, [])
    attempts = [t for t in attempts if current_time - t < BLOCK_TIME]
    attempts.append(current_time)
    failed_attempts[ip] = attempts

def clear_failed_attempts(ip: str):
    """Limpa as tentativas falhadas para um IP após login bem-sucedido"""
    if ip in failed_attempts:
        del failed_attempts[ip]

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
