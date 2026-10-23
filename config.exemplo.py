# Copie este arquivo para config.py e ajuste os valores da sua máquina.
# O config.py fica fora do Git porque guarda a senha do banco e a SECRET_KEY.

# Chave que o Django usa para assinar dados. Gere uma nova com:
#   python -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY = 'troque-por-uma-chave-gerada'

# Com DEBUG ligado, um erro mostra o código e as variáveis no navegador.
# Deixe False em qualquer máquina acessível por outras pessoas.
DEBUG = False

# Nomes pelos quais o site pode ser acessado. Pedido com outro nome no
# cabeçalho Host recebe 400.
ENDERECOS_ACEITOS = ['localhost', '127.0.0.1']

BANCO = {
    'host': 'localhost',
    'porta': 5432,
    'nome': 'mini_mural',
    # Usuário próprio da aplicação, criado no passo de instalação do banco
    # (README).
    'usuario': 'mini_mural',
    'senha': 'troque-pela-senha-escolhida',
}

# Fuso usado para mostrar a hora dos recados.
FUSO_HORARIO = 'America/Araguaina'
