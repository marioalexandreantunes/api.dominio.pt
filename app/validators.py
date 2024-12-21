from functools import wraps
from flask import request, jsonify

class ValidateError(Exception):
    pass

class Validator:
    def __init__(self):
        pass

class UserValidator(Validator):
    def __init__(self):
        super().__init__()
        
    def validate_registration(self, data):
        errors = []
        
        # Validar email
        if not data.get('email'):
            errors.append("O email é obrigatório")
        elif not self._is_valid_email(data['email']):
            errors.append("Formato de email inválido")
            
        # Validar palavra-passe
        if not data.get('password'):
            errors.append("A palavra-passe é obrigatória")
        elif len(data['password']) < 8:
            errors.append("A palavra-passe deve ter pelo menos 8 caracteres")
        elif not any(char.isdigit() for char in data['password']):
            errors.append("A palavra-passe deve conter pelo menos um número")
        elif not any(char.isupper() for char in data['password']):
            errors.append("A palavra-passe deve conter pelo menos uma letra maiúscula")
            
        # Validar nome se fornecido
        if 'name' in data and not data['name']:
            errors.append("O nome não pode estar vazio se fornecido")
            
        if errors:
            raise ValidateError(errors)
            
    def validate_login(self, data):
        errors = []
        
        # Validar email
        if not data.get('email'):
            errors.append("O email é obrigatório")
        elif not self._is_valid_email(data['email']):
            errors.append("Formato de email inválido")
            
        # Validar palavra-passe
        if not data.get('password'):
            errors.append("A palavra-passe é obrigatória")
            
        if errors:
            raise ValidateError(errors)
            
    def _is_valid_email(self, email):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

# Criar instância do validador
user_validator = UserValidator()

# Decorador para validação de pedidos
def validate_request(validation_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                if validation_type == 'registration':
                    user_validator.validate_registration(data)
                elif validation_type == 'login':
                    user_validator.validate_login(data)
                return f(*args, **kwargs)
            except ValidateError as e:
                return jsonify({
                    'status': 'error',
                    'message': 'A validação falhou',
                    'errors': e.args[0]
                }), 400
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Dados do pedido inválidos',
                    'error': str(e)
                }), 400
        return decorated_function
    return decorator
