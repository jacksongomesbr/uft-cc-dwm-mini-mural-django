"""Todo acesso à tabela recados mora neste arquivo.

As views chamam estas funções e não montam consultas.
"""
from .models import Recado


def listar_recados(ordem):
    """Lista todos os recados na ordem escolhida.

    A ordem vem de uma lista fechada: o valor do cookie decide entre duas
    strings fixas e nunca chega ao banco.
    """
    # select_related traz o autor na mesma consulta, com um JOIN. Sem ele, o
    # template faria uma consulta a mais por recado ao mostrar o nome.
    recados = Recado.objects.select_related('autor')
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


def arquivar_recado(id):
    """Arquiva um recado publicado.

    O filtro por status torna a operação repetível: arquivar duas vezes, ou
    arquivar um id que não existe, não altera nenhuma linha e não gera erro.
    """
    Recado.objects.filter(id=id, status=Recado.PUBLICADO).update(
        status=Recado.ARQUIVADO
    )


def resumir_recados(recados):
    """Conta publicados e arquivados de uma lista já carregada."""
    publicados = sum(1 for recado in recados if not recado.arquivado)
    return {'publicados': publicados, 'arquivados': len(recados) - publicados}
