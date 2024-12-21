template = {
    "swagger": "2.0",
    "info": {
        "title": "API marioCodeLabs 2024",
        "description": "API de autenticação e gerenciamento de usuários",
        "version": "1.0"
    },
    "basePath": "/api/v1",
    "schemes": [
        "http",
        "https"
    ],
    "paths": {
        "/": {
            "get": {
                "tags": ["Status"],
                "summary": "Verifica o status da API",
                "description": "Retorna o status da API e da conexão com o banco de dados",
                "responses": {
                    "200": {
                        "description": "Status OK"
                    },
                    "500": {
                        "description": "Status OFF"
                    }
                }
            }
        },
        "/createsuperuser": {
            "post": {
                "tags": ["Usuários"],
                "summary": "Cria o primeiro usuário administrador",
                "description": "Cria o superusuário apenas se não existir nenhum usuário no sistema",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "description": "Must be a valid email address",
                                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                                    "example": "user@example.com"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "Password must be at least 8 characters long, contain at least one number and one uppercase letter",
                                    "minLength": 8,
                                    "pattern": "^(?=.*[A-Z])(?=.*\\d).+$",
                                    "example": "Password123"
                                }
                            }
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Usuário criado com sucesso"
                    },
                    "400": {
                        "description": "Validation failed (invalid email format, password requirements not met)"
                    },
                    "409": {
                        "description": "Usuário já existe"
                    }
                }
            }
        },
        "/login": {
            "post": {
                "tags": ["Autenticação"],
                "summary": "Autenticação de usuário",
                "description": "Retorna um token JWT válido por 7 minutos",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "description": "Must be a valid email address",
                                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                                    "example": "user@example.com"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "Password must be at least 8 characters long, contain at least one number and one uppercase letter",
                                    "minLength": 8,
                                    "pattern": "^(?=.*[A-Z])(?=.*\\d).+$",
                                    "example": "Password123"
                                },
                                "name": {
                                    "type": "string",
                                    "description": "Optional user name. If provided, cannot be empty",
                                    "minLength": 1
                                }
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Login realizado com sucesso"
                    },
                    "400": {
                        "description": "Validation failed (invalid email format)"
                    },
                    "401": {
                        "description": "Email ou senha incorretos"
                    }
                }
            }
        },
        "/cadastro": {
            "post": {
                "tags": ["Usuários"],
                "summary": "Cadastra novo usuário",
                "description": "Requer autenticação JWT",
                "parameters": [
                    {
                        "name": "Authorization",
                        "in": "header",
                        "type": "string",
                        "required": True,
                        "description": "Bearer {token}"
                    },
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "description": "Must be a valid email address",
                                    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                                    "example": "user@example.com"
                                },
                                "password": {
                                    "type": "string",
                                    "description": "Password must be at least 8 characters long, contain at least one number and one uppercase letter",
                                    "minLength": 8,
                                    "pattern": "^(?=.*[A-Z])(?=.*\\d).+$",
                                    "example": "Password123"
                                }
                            }
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Usuário criado com sucesso"
                    },
                    "400": {
                        "description": "Validation failed (invalid email format, password requirements not met)"
                    },
                    "409": {
                        "description": "Email já existe"
                    }
                }
            }
        },
        "/cadastros": {
            "get": {
                "tags": ["Usuários"],
                "summary": "Lista todos os usuários",
                "description": "Requer autenticação JWT",
                "parameters": [
                    {
                        "name": "Authorization",
                        "in": "header",
                        "type": "string",
                        "required": True,
                        "description": "Bearer {token}"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Lista de usuários retornada com sucesso"
                    },
                    "404": {
                        "description": "Nenhum usuário encontrado"
                    }
                }
            }
        }
    }
}
