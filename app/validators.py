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
        
        # Validate email
        if not data.get('email'):
            errors.append("Email is required")
        elif not self._is_valid_email(data['email']):
            errors.append("Invalid email format")
            
        # Validate password
        if not data.get('password'):
            errors.append("Password is required")
        elif len(data['password']) < 8:
            errors.append("Password must be at least 8 characters long")
        elif not any(char.isdigit() for char in data['password']):
            errors.append("Password must contain at least one number")
        elif not any(char.isupper() for char in data['password']):
            errors.append("Password must contain at least one uppercase letter")
            
        # Validate name if required
        if 'name' in data and not data['name']:
            errors.append("Name cannot be empty if provided")
            
        if errors:
            raise ValidateError(errors)
            
    def validate_login(self, data):
        errors = []
        
        # Validate email
        if not data.get('email'):
            errors.append("Email is required")
        elif not self._is_valid_email(data['email']):
            errors.append("Invalid email format")
            
        # Validate password
        if not data.get('password'):
            errors.append("Password is required")
            
        if errors:
            raise ValidateError(errors)
            
    def _is_valid_email(self, email):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

# Create validator instance
user_validator = UserValidator()

# Decorator for request validation
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
                    'message': 'Validation failed',
                    'errors': e.args[0]
                }), 400
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid request data',
                    'error': str(e)
                }), 400
        return decorated_function
    return decorator
