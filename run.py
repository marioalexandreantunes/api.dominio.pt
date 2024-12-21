# Importações necessárias
import logging  # Para registro de logs
import os      # Para variáveis de ambiente

# Importações da aplicação e servidores
from app import api  # Importa a aplicação Flask
from dotenv import load_dotenv  # Para carregar variáveis de ambiente
from gevent.pywsgi import WSGIServer  # Servidor WSGI para produção

# Carrega configurações do ambiente
load_dotenv()
debug = os.getenv("DEBUG") == "True"  # Modo de desenvolvimento ou produção


if __name__ == "__main__":
    # Configuração do sistema de logs
    # Formato: Data/Hora - Nível - Mensagem
    logging.basicConfig(
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        level=logging.INFO,  # Nível de log definido como INFO
    )
    
    logging.info("Iniciando a aplicação...")
    
    # Configuração da porta do servidor
    # Usa PORT_DEBUG do .env ou 5000 como padrão
    port = int(os.getenv("PORT_DEBUG", 5000))
    host = "127.0.0.1" if debug else "0.0.0.0"
    
    logging.info(f"Servidor configurado em {host}:{port}")
    
    # Inicia o servidor apropriado baseado no modo de execução
    server_info = f"Servidor API: http://{host}:{port}/api/v1/\nDocumentação: http://{host}:{port}/api/docs/"
    logging.info(server_info)
    
    if debug:
        # Modo desenvolvimento: usa o servidor de desenvolvimento do Flask
        api.run(host=host, port=port, debug=debug)
    else:
        # Modo produção: usa o servidor WSGI (gevent)
        server = WSGIServer((host, port), api)
        server.serve_forever()