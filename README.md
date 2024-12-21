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
- Configuração de variáveis sensíveis via arquivo .env
- Inclusão do .env no .gitignore para proteção de credenciais
- Documentação clara sobre configurações de segurança
- Sistema robusto de rate limiting com limites específicos por rota:
  - Limites base: 100/dia, 30/hora, 5/minuto
  - Limites personalizados para endpoints sensíveis
  - Headers informativos sobre limites e tempo de espera
- Proteção avançada contra ataques de força bruta:
  - Bloqueio de IP após 3 tentativas falhadas
  - Tempo de bloqueio de 30 minutos
  - Limpeza automática de tentativas antigas
  - Logging de tentativas suspeitas
- Sistema de logging detalhado para auditoria de segurança
- Proteção contra ataques XSS através de sanitização de inputs
- Hash seguro de senhas com bcrypt

### ⚠️ Pontos a Melhorar
- Implementar refresh tokens para melhor gestão de sessões
- Configurar CORS de forma mais restritiva
- Adicionar validação adicional para inputs complexos
- Implementar sistema de backup seguro para a base de dados
- Adicionar monitorização de segurança em tempo real

## ⚙️ Configuração do Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Configuração da Base de Dados MongoDB
DATABASE_URL="sua_url_de_conexao_mongodb"

# Configuração do Servidor
PORT_DEBUG=5000    # Porta onde o servidor irá executar
DEBUG=true         # Modo de debug (true/false)

# Configuração JWT
JWT_SECRET_KEY=sua_chave_secreta_jwt_muito_segura    # Chave secreta para assinatura dos tokens
TOKEN_HEADER_KEY=x-access-token                      # Nome do header para o token JWT
```

**Importante**:
1. Substitua `sua_url_de_conexao_mongodb` pela URL de conexão do seu cluster MongoDB
2. Gere uma chave secreta forte para `JWT_SECRET_KEY` (recomendado: mínimo 64 caracteres)
3. Nunca compartilhe seu arquivo `.env` ou credenciais sensíveis
4. Certifique-se de que o `.env` está incluído no `.gitignore`

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter um Pull Request.

## 📄 Licença

Este projeto está sob a licença MIT. Consulte o ficheiro LICENSE para mais detalhes.
