"""Ordem do mural, guardada em cookie.

A ordem é uma preferência de quem usa o navegador, e fica em cookie. Com o
login, ela poderia ir para o banco, por usuário; continua no cookie para manter
o comportamento das etapas anteriores (decisão D11).
"""

COOKIE_DA_ORDEM = 'mini_mural_ordem'

ORDENS = {
    'mais-recentes': 'Mais recentes primeiro',
    'mais-antigos': 'Mais antigos primeiro',
}

UM_ANO_EM_SEGUNDOS = 60 * 60 * 24 * 365


def ler_ordem(request):
    """Lê a ordem do cookie. Valor ausente ou desconhecido vira a padrão."""
    valor = request.COOKIES.get(COOKIE_DA_ORDEM, '')
    return 'mais-antigos' if valor == 'mais-antigos' else 'mais-recentes'


def salvar_ordem(response, ordem):
    """Grava a ordem em um cookie que dura um ano."""
    response.set_cookie(
        COOKIE_DA_ORDEM,
        ordem,
        max_age=UM_ANO_EM_SEGUNDOS,
        httponly=True,
        samesite='Lax',
    )


def ordem_valida(ordem):
    return ordem in ORDENS
