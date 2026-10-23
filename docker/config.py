# Configuração usada dentro do contêiner, no lugar do config.py local. Os
# valores vêm das variáveis de ambiente definidas em compose.yaml.
import os

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False
ENDERECOS_ACEITOS = ['localhost', '127.0.0.1']

BANCO = {
    # Nome do serviço do banco em compose.yaml. Dentro da rede do Compose,
    # cada serviço é encontrado pelo próprio nome.
    'host': os.environ['BANCO_HOST'],
    'porta': int(os.environ['BANCO_PORTA']),
    'nome': os.environ['BANCO_NOME'],
    'usuario': os.environ['BANCO_USUARIO'],
    'senha': os.environ['BANCO_SENHA'],
}

FUSO_HORARIO = 'America/Araguaina'
