"""python manage.py carregar_esquema [--exemplos] [--se-ausente]

Cria a tabela recados a partir de sql/schema.sql. Roda depois do migrate,
porque a tabela aponta para auth_user, criada pelas migrations do Django.
"""
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection

PASTA_SQL = Path(settings.PASTA_DO_PROJETO) / 'sql'

USUARIO_DE_EXEMPLO = 'exemplo'
SENHA_DE_EXEMPLO = 'senha-de-exemplo'


def executar_arquivo(nome):
    """Executa um arquivo de sql/ inteiro, com todos os comandos dele.

    Sem parâmetros, o psycopg aceita vários comandos separados por ";" em uma
    chamada só, como o psql -f.
    """
    with connection.cursor() as cursor:
        cursor.execute((PASTA_SQL / nome).read_text(encoding='utf-8'))


class Command(BaseCommand):
    help = 'Cria a tabela recados a partir de sql/schema.sql.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--exemplos',
            action='store_true',
            help='Cria também o usuário exemplo e os recados de sql/seed.sql.',
        )
        parser.add_argument(
            '--se-ausente',
            action='store_true',
            help='Não faz nada se a tabela recados já existe. Sem esta opção, '
                 'a tabela é recriada e os recados se perdem.',
        )

    def handle(self, *args, exemplos, se_ausente, **opcoes):
        if se_ausente and 'recados' in connection.introspection.table_names():
            self.stdout.write('A tabela recados já existe; nada foi alterado.')
            return

        executar_arquivo('schema.sql')
        self.stdout.write('Tabela recados criada.')

        if exemplos:
            Usuario = get_user_model()
            if not Usuario.objects.filter(username=USUARIO_DE_EXEMPLO).exists():
                # create_user grava o hash da senha, nunca a senha.
                Usuario.objects.create_user(USUARIO_DE_EXEMPLO, password=SENHA_DE_EXEMPLO)
            executar_arquivo('seed.sql')
            self.stdout.write(
                f'Recados de exemplo criados. Usuário: {USUARIO_DE_EXEMPLO}, '
                f'senha: {SENHA_DE_EXEMPLO}.'
            )
