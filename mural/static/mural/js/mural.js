// Comportamento do formulário de recado no navegador.
//
// Este arquivo só melhora a experiência: avisa o erro antes do envio, devolve
// o foco ao campo e atualiza o contador. Sem ele, o formulário continua
// funcionando, e o Django faz a mesma validação em mural/validacao.py.

const formulario = document.querySelector('[data-novo-recado]');

if (formulario) {
  const campo = formulario.querySelector('textarea');
  const mensagem = formulario.querySelector('#erro-texto');
  const contador = formulario.querySelector('#contador');
  const limite = Number(formulario.dataset.limite);

  // Só mostra erro depois que a pessoa saiu do campo ou tentou publicar.
  // Se a página já voltou do servidor com erro, o campo conta como tocado.
  let tocouNoCampo = campo.getAttribute('aria-invalid') === 'true';

  // Mesmas mensagens de validar_recado(), em mural/validacao.py.
  function validar(texto) {
    const textoLimpo = texto.trim();
    if (textoLimpo.length === 0) {
      return 'Escreva o recado antes de publicar.';
    }
    if (textoLimpo.length > limite) {
      return `O recado aceita até ${limite} caracteres.`;
    }
    return '';
  }

  function mostrarErro() {
    const erro = tocouNoCampo ? validar(campo.value) : '';
    mensagem.textContent = erro;
    if (erro) {
      campo.setAttribute('aria-invalid', 'true');
    } else {
      campo.removeAttribute('aria-invalid');
    }
    return erro;
  }

  function atualizarContador() {
    const restantes = limite - campo.value.length;
    contador.textContent = `${restantes} caracteres restantes`;
    contador.classList.toggle('perto-do-limite', restantes <= 20);
  }

  campo.addEventListener('input', () => {
    atualizarContador();
    mostrarErro();
  });

  campo.addEventListener('blur', () => {
    tocouNoCampo = true;
    mostrarErro();
  });

  // O botão fica sempre habilitado: publicar vazio mostra a orientação.
  formulario.addEventListener('submit', (evento) => {
    tocouNoCampo = true;
    if (mostrarErro()) {
      evento.preventDefault();
      campo.focus();
    }
  });
}
