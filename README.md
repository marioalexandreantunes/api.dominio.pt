# API RESTful - dominio.pt

Uma API RESTful robusta desenvolvida com Python e Flask, implementando autenticação JWT, base de dados MongoDB e documentação Swagger.

## 🚀 Tecnologias Utilizadas

- Python
- Flask (Framework Web)
- JWT (JSON Web Tokens para autenticação)
- MongoDB (Base de dados)
- Swagger (Documentação da API)

## 📋 Pré-requisitos

- Python 3.12+
- MongoDB instalado e em execução
- pip (gestor de pacotes Python)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/api.dominio.pt.git
cd api.dominio.pt
```

2. Crie um ambiente virtual:
```bash
python -m venv env312
```

3. Ative o ambiente virtual:
- Windows:
```bash
env312\Scripts\activate
```
- Linux/Mac:
```bash
source env312/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

## ⚡ Como Executar

1. Certifique-se que o MongoDB está em execução
2. Ative o ambiente virtual (se ainda não estiver ativo)
3. Execute o servidor:
```bash
python run.py
```

O servidor iniciará por defeito em `http://localhost:5000`

## 📁 Estrutura do Projeto

```
api.dominio.pt/
├── app/
│   ├── __init__.py    # Inicialização da aplicação Flask
│   ├── routes.py      # Rotas da API
│   ├── swagger.py     # Configuração do Swagger
│   ├── utils.py       # Funções utilitárias
│   └── validators.py  # Validadores de dados
├── requirements.txt   # Dependências do projeto
└── run.py            # Ponto de entrada da aplicação
```

## 📚 Documentação da API

A documentação completa da API está disponível através do Swagger UI após iniciar o servidor:

`http://localhost:5000/api/docs`

## 🔐 Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. Para aceder aos endpoints protegidos, é necessário:

1. Obter um token através do endpoint de autenticação
2. Incluir o token no header das requisições:
```
Authorization: Bearer <seu-token>
```

## 🛡️ Análise de Segurança

### ✅ Pontos Positivos
- Implementação de JWT para autenticação segura
- Validação de dados nos endpoints através de validators
- Ambiente virtual isolado para dependências
- Utilização de HTTPS para comunicação segura
- Estrutura modular que facilita a manutenção segura

### ⚠️ Pontos a Melhorar
- Implementar rate limiting para prevenir ataques de força bruta
- Adicionar logging detalhado para auditoria de segurança
- Implementar refresh tokens para melhor gestão de sessões
- Configurar CORS de forma mais restritiva
- Adicionar validação adicional para inputs complexos

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter um Pull Request.

## 📄 Licença

Este projeto está sob a licença MIT. Consulte o ficheiro LICENSE para mais detalhes.
