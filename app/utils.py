import datetime
from flask import jsonify

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
