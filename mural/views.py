"""As views do mural. Cada uma recebe um pedido e devolve uma resposta.

GET mostra a página; POST grava e redireciona (POST/redirect/GET). Todas
exigem login, menos o detalhe de um recado público e as telas de entrar e de
criar conta.
"""
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, redirect_to_login
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


@login_required
@require_http_methods(['GET', 'POST'])
def mural(request):
    """Lista os recados, mostra o resumo e recebe o formulário de recado novo.

    O @login_required manda quem não entrou para a tela de login (LOGIN_URL,
    em settings.py), com o endereço pedido no parâmetro next.
    """
    texto = ''
    publico = False
    erro = None
    status = 200

    if request.method == 'POST':
        texto = normalizar_quebras_de_linha(request.POST.get('texto', ''))
        # Caixa desmarcada não é enviada pelo navegador; ausente quer dizer privado.
        publico = request.POST.get('publico') == '1'
        erro = validar_recado(texto)

        if erro is None:
            recados.publicar_recado(texto.strip(), request.user, publico)
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
        'publico': publico,
        'erro': erro,
        'limite': LIMITE_DO_RECADO,
        'restantes': restantes,
        'perto_do_limite': restantes <= 20,
    }, status=status)


@require_http_methods(['GET'])
def recado(request, id):
    """Detalhe de um recado: /recado/42/

    É a única view do mural que atende quem não entrou, e só para recado
    público. Nesse caso o template mostra o recado sem o botão de arquivar.

    O conversor <int:id> em urls.py só deixa chegar aqui um número. Um id que
    não é número nem chama esta view: o Django responde 404 antes.
    """
    encontrado = recados.buscar_recado(id)
    if encontrado is None:
        return render(request, 'mural/nao_encontrado.html', status=404)

    # Recado privado só para quem entrou. Quem não entrou vai para o login e,
    # depois dele, volta a este endereço.
    if not encontrado.publico and not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    return render(request, 'mural/recado.html', {
        'pagina_atual': 'mural',
        'recado': encontrado,
    })


@login_required
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


@login_required
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


class Entrar(LoginView):
    """Tela de login do Django, com o template do mural.

    A LoginView confere usuário e senha, troca o identificador da sessão e
    segue o parâmetro next só se ele apontar para este mesmo site. A única
    mudança é responder 422, e não 200, quando o login falha.
    """

    template_name = 'mural/entrar.html'
    redirect_authenticated_user = True
    extra_context = {'pagina_atual': 'entrar'}

    def form_invalid(self, form):
        resposta = super().form_invalid(form)
        resposta.status_code = 422
        return resposta


@require_http_methods(['GET', 'POST'])
def cadastro(request):
    """Cria uma conta e já faz o login com ela.

    O UserCreationForm do Django confere se o nome já existe (sem diferenciar
    maiúsculas de minúsculas), aplica as regras de senha de
    AUTH_PASSWORD_VALIDATORS e grava só o hash da senha.
    """
    if request.user.is_authenticated:
        return redirecionar(reverse('mural'))

    form = UserCreationForm(request.POST or None)
    status = 200

    if request.method == 'POST':
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirecionar(reverse('mural'))
        status = 422

    return render(request, 'mural/cadastro.html', {
        'pagina_atual': 'cadastro',
        'form': form,
    }, status=status)
