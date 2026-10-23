"""Testes das regras que não dependem de banco.

Rode com: python manage.py test

SimpleTestCase não abre conexão com o banco. Isso importa aqui: a tabela
recados vem do schema.sql, e o banco de teste que o Django criaria não a
teria.
"""
from datetime import datetime, timezone

from django.contrib.auth.models import AnonymousUser, User
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase

from .models import Recado
from .preferencias import COOKIE_DA_ORDEM, ler_ordem
from .recados import resumir_recados
from .validacao import normalizar_quebras_de_linha, validar_recado


class ValidarRecadoTest(SimpleTestCase):
    def test_texto_vazio_e_recusado(self):
        self.assertEqual(validar_recado(''), 'Escreva o recado antes de publicar.')

    def test_so_espacos_e_recusado(self):
        self.assertEqual(validar_recado('  \n '), 'Escreva o recado antes de publicar.')

    def test_texto_comum_e_aceito(self):
        self.assertIsNone(validar_recado('Reunião às 14h.'))

    def test_280_caracteres_acentuados_e_aceito(self):
        self.assertIsNone(validar_recado('á' * 280))

    def test_281_caracteres_e_recusado(self):
        self.assertEqual(validar_recado('a' * 281), 'O recado aceita até 280 caracteres.')

    def test_espacos_nas_pontas_nao_contam(self):
        self.assertIsNone(validar_recado('  ' + 'a' * 280 + '  '))

    def test_quebra_de_linha_do_navegador_vira_uma(self):
        self.assertEqual(normalizar_quebras_de_linha('a\r\nb'), 'a\nb')


class LerOrdemTest(SimpleTestCase):
    def pedido_com_cookie(self, valor=None):
        request = RequestFactory().get('/')
        if valor is not None:
            request.COOKIES[COOKIE_DA_ORDEM] = valor
        return request

    def test_sem_cookie_mais_recentes(self):
        self.assertEqual(ler_ordem(self.pedido_com_cookie()), 'mais-recentes')

    def test_cookie_mais_antigos(self):
        self.assertEqual(ler_ordem(self.pedido_com_cookie('mais-antigos')), 'mais-antigos')

    def test_cookie_desconhecido_mais_recentes(self):
        pedido = self.pedido_com_cookie("'; DROP TABLE recados; --")
        self.assertEqual(ler_ordem(pedido), 'mais-recentes')


class FormatacaoTest(SimpleTestCase):
    """O banco devolve o instante em UTC; a tela mostra no fuso de Araguaína."""

    instante = datetime(2026, 3, 12, 17, 2, tzinfo=timezone.utc)

    def renderizar(self, trecho):
        return Template(trecho).render(Context({'c': self.instante})).strip()

    def test_hora_no_fuso_local(self):
        self.assertEqual(self.renderizar("{{ c|date:'H:i' }}"), '14:02')

    def test_data_e_hora_por_extenso(self):
        trecho = r"{{ c|date:'j \d\e F \d\e Y \à\s H:i'|lower }}"
        self.assertEqual(self.renderizar(trecho), '12 de março de 2026 às 14:02')


class ResumirRecadosTest(SimpleTestCase):
    def test_conta_publicados_e_arquivados(self):
        lista = [
            Recado(status=Recado.PUBLICADO),
            Recado(status=Recado.PUBLICADO),
            Recado(status=Recado.ARQUIVADO),
        ]
        self.assertEqual(resumir_recados(lista), {'publicados': 2, 'arquivados': 1})

    def test_lista_vazia(self):
        self.assertEqual(resumir_recados([]), {'publicados': 0, 'arquivados': 0})


class RegrasDoRecadoTest(SimpleTestCase):
    """leitura_publica e pode_ser_arquivado_por, sem banco."""

    def setUp(self):
        self.ana = User(id=7, username='ana')
        self.recado = Recado(autor=self.ana, status=Recado.PUBLICADO, publico=True)

    def test_autor_arquiva_o_proprio_recado(self):
        self.assertTrue(self.recado.pode_ser_arquivado_por(self.ana))

    def test_outro_usuario_nao_arquiva(self):
        self.assertFalse(self.recado.pode_ser_arquivado_por(User(id=8, username='bia')))

    def test_sem_login_nao_arquiva(self):
        self.assertFalse(self.recado.pode_ser_arquivado_por(AnonymousUser()))

    def test_recado_arquivado_nao_arquiva_de_novo(self):
        self.recado.status = Recado.ARQUIVADO
        self.assertFalse(self.recado.pode_ser_arquivado_por(self.ana))

    def test_publico_e_publicado_tem_leitura_publica(self):
        self.assertTrue(self.recado.leitura_publica)

    def test_privado_nao_tem_leitura_publica(self):
        self.recado.publico = False
        self.assertFalse(self.recado.leitura_publica)

    def test_publico_arquivado_nao_tem_leitura_publica(self):
        self.recado.status = Recado.ARQUIVADO
        self.assertFalse(self.recado.leitura_publica)
