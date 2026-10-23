"""Todo acesso à tabela recados mora neste arquivo.

As views chamam estas funções e não montam consultas.
"""
from django.db.models import Q
from django.db.models.functions import Now

from .models import Recado


def listar_recados(ordem, usuario):
    """Lista os recados que o usuário logado vê, na ordem escolhida: os
    publicados de todos e os arquivados só dele.

    A ordem vem de uma lista fechada: o valor do cookie decide entre duas
    strings fixas e nunca chega ao banco.
    """
    # select_related traz o autor na mesma consulta, com um JOIN. Sem ele, o
    # template faria uma consulta a mais por recado ao mostrar o nome.
    # Q junta condições com | (OU) em uma consulta só.
    recados = Recado.objects.select_related('autor').filter(
        Q(status=Recado.PUBLICADO) | Q(autor=usuario)
    )
    if ordem == 'mais-antigos':
        return list(recados.order_by('criado_em', 'id'))
    return list(recados.order_by('-criado_em', '-id'))


def listar_recados_publicos(ordem):
    """Lista só os recados que qualquer pessoa pode ler: públicos e ainda
    publicados. É a lista de quem não entrou."""
    recados = Recado.objects.select_related('autor').filter(
        publico=True, status=Recado.PUBLICADO
    )
    if ordem == 'mais-antigos':
        return list(recados.order_by('criado_em', 'id'))
    return list(recados.order_by('-criado_em', '-id'))


def buscar_recado(id):
    """Devolve o recado com esse id, ou None se ele não existe."""
    return Recado.objects.select_related('autor').filter(id=id).first()


def publicar_recado(texto, autor, publico):
    """Grava um recado novo.

    Data e status vêm dos valores padrão da tabela. Quem chama já validou o
    texto com validar_recado().
    """
    Recado.objects.create(texto=texto, autor=autor, publico=publico)


def arquivar_recado(id, autor):
    """Arquiva um recado publicado do autor e grava o instante do arquivamento.

    O filtro por autor repete, no banco, a regra que a view já conferiu com
    pode_ser_arquivado_por(). O filtro por status torna a operação repetível:
    arquivar duas vezes não altera nada na segunda, e a data do primeiro
    arquivamento fica.
    """
    Recado.objects.filter(id=id, autor=autor, status=Recado.PUBLICADO).update(
        status=Recado.ARQUIVADO, arquivado_em=Now()
    )


def resumir_recados(recados):
    """Conta publicados e arquivados de uma lista já carregada."""
    publicados = sum(1 for recado in recados if not recado.arquivado)
    return {'publicados': publicados, 'arquivados': len(recados) - publicados}
