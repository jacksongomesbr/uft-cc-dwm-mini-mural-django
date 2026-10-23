"""As quatro views do mural. Cada uma recebe um pedido e devolve uma resposta.

GET mostra a página; POST grava e redireciona (POST/redirect/GET).
"""
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from . import recados
from .preferencias import ORDENS, ler_ordem, ordem_valida, salvar_ordem
from .validacao import LIMITE_DO_RECADO, normalizar_quebras_de_linha, validar_recado


def redirecionar(endereco):
    """Manda o navegador para outra página com o código 303.

    É o passo final do padrão POST/redirect/GET: depois de gravar, o navegador
    faz um GET novo, e recarregar a página não reenvia o formulário. O
    redirect() do Django responde 302; o 303 deixa explícito que o pedido
    seguinte é um GET.
    """
    resposta = HttpResponseRedirect(endereco)
    resposta.status_code = 303
    return resposta


@require_http_methods(['GET', 'POST'])
def mural(request):
    """Lista os recados, mostra o resumo e recebe o formulário de recado novo."""
    texto = ''
    erro = None
    status = 200

    if request.method == 'POST':
        texto = normalizar_quebras_de_linha(request.POST.get('texto', ''))
        erro = validar_recado(texto)

        if erro is None:
            recados.publicar_recado(texto.strip())
            return redirecionar(reverse('mural'))

        # Texto inválido: a página é mostrada de novo, com a mensagem e com o
        # que a pessoa digitou. O código 422 diz que o pedido foi recusado.
        status = 422

    lista = recados.listar_recados(ler_ordem(request))
    restantes = LIMITE_DO_RECADO - len(texto)

    return render(request, 'mural/mural.html', {
        'pagina_atual': 'mural',
        'recados': lista,
        'resumo': recados.resumir_recados(lista),
        'texto': texto,
        'erro': erro,
        'limite': LIMITE_DO_RECADO,
        'restantes': restantes,
        'perto_do_limite': restantes <= 20,
    }, status=status)


@require_http_methods(['GET'])
def recado(request, id):
    """Detalhe de um recado: /recado/42/

    O conversor <int:id> em urls.py só deixa chegar aqui um número. Um id que
    não é número nem chama esta view: o Django responde 404 antes.
    """
    encontrado = recados.buscar_recado(id)
    if encontrado is None:
        return render(request, 'mural/nao_encontrado.html', status=404)

    return render(request, 'mural/recado.html', {
        'pagina_atual': 'mural',
        'recado': encontrado,
    })


@require_POST
def arquivar(request, id):
    """Recebe o botão "Arquivar" da lista e do detalhe.

    Mudança de dados só por POST: o @require_POST responde 405 a um GET. Um
    link que arquivasse poderia ser disparado por um buscador ou por uma
    pré-carga do navegador.
    """
    recados.arquivar_recado(id)

    # O destino sai de duas opções fixas. Aceitar um endereço qualquer vindo
    # do formulário deixaria um site externo usar este para redirecionar
    # pessoas.
    if request.POST.get('voltar_para') == 'detalhe':
        return redirecionar(reverse('recado', args=[id]))

    # Na lista, a âncora devolve a pessoa ao recado que ela acabou de arquivar.
    return redirecionar(reverse('mural') + f'#recado-{id}')


@require_http_methods(['GET', 'POST'])
def sobre(request):
    """Informações do projeto e escolha da ordem do mural.

    Esta view não usa o banco: a ordem fica em um cookie do navegador.
    """
    erro = None
    status = 200

    if request.method == 'POST':
        ordem_escolhida = request.POST.get('ordem', '')

        if ordem_valida(ordem_escolhida):
            resposta = redirecionar(reverse('sobre') + '?salvo=1')
            salvar_ordem(resposta, ordem_escolhida)
            return resposta

        status = 422
        erro = 'Escolha uma das ordens da lista.'

    return render(request, 'mural/sobre.html', {
        'pagina_atual': 'sobre',
        'ordens': ORDENS,
        'ordem': ler_ordem(request),
        'salvo': 'salvo' in request.GET,
        'erro': erro,
    }, status=status)
