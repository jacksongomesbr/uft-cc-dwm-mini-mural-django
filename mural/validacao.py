LIMITE_DO_RECADO = 280


def validar_recado(texto, limite=LIMITE_DO_RECADO):
    """Confere o texto de um recado e devolve a mensagem de erro, ou None se
    o texto é válido.

    Esta é a regra que vale. O JavaScript do navegador repete a conferência só
    para avisar mais cedo; um pedido que chega sem passar por ele é conferido
    aqui do mesmo jeito.
    """
    texto_limpo = texto.strip()

    if not texto_limpo:
        return 'Escreva o recado antes de publicar.'

    if len(texto_limpo) > limite:
        return f'O recado aceita até {limite} caracteres.'

    return None


def normalizar_quebras_de_linha(texto):
    """O navegador envia cada quebra de linha do textarea como \\r\\n, dois
    caracteres, mas o atributo maxlength conta como um. Trocar por \\n faz o
    Python contar igual ao navegador.
    """
    return texto.replace('\r\n', '\n')
