# Decisões de projeto

Cada decisão abaixo registra o que foi escolhido, a alternativa descartada e a
consequência que a equipe aceitou ao escolher. Sem a alternativa descartada, o
registro vira descrição do código; sem a consequência, ele esconde o custo de
quem vier mexer no código depois.

O objetivo do projeto orienta todas elas: mostrar a versão mais simples de uma
aplicação web com Django e banco de dados, legível para quem está no 4º ou 5º
período.

Os números não mudam de uma etapa para outra, para você poder comparar os
ramos. Quando uma etapa revê uma decisão anterior, a decisão antiga ganha uma
nota que aponta para a nova, e a nova entra no fim do documento.

## Arquitetura

### D1. Monólito com HTML montado no servidor

- **Decisão:** um único projeto Django recebe o pedido, consulta o banco e
  devolve a página HTML pronta, montada por templates. O navegador recebe HTML,
  CSS e um JavaScript pequeno.
- **Alternativa descartada:** uma API JSON com Django REST Framework e uma
  página que monta a tela com JavaScript (`fetch`).
- **Motivo:** com HTML montado no servidor, o caminho de cada funcionalidade
  passa por uma view e um template, e o aluno vê a requisição inteira sem
  precisar de duas bases de código.
- **Consequência aceita:** toda ação recarrega a página inteira. Um app mobile
  não consegue reaproveitar o servidor, porque ele devolve HTML em vez de
  dados; para isso seria preciso acrescentar views que respondam JSON.

### D2. Views em funções

- **Decisão:** `mural/views.py` tem quatro funções, uma por endereço. Cada uma
  testa `request.method` e decide o que fazer com GET e com POST.
- **Alternativa descartada:** views em classes, como `ListView`, `DetailView`
  e `FormView`.
- **Motivo:** a função mostra, de cima a baixo, o pedido entrando e a resposta
  saindo. As views em classes escondem esse caminho em métodos herdados, que o
  aluno precisaria conhecer antes de ler o código.
- **Consequência aceita:** cada view repete o `if request.method == 'POST'`, e
  a lógica de mostrar a página de novo com erro é escrita à mão.

### D3. Endereços no URLconf, com o id no caminho

- **Decisão:** `mural/urls.py` liga cada endereço a uma view:
  `/`, `/recado/<int:id>/`, `/recado/<int:id>/arquivar/` e `/sobre/`. Templates
  e views montam os endereços pelo nome, com `{% url %}` e `reverse()`.
- **Alternativa descartada:** o id na query string (`/recado/?id=42`), lido e
  convertido dentro da view.
- **Motivo:** o conversor `<int:id>` recusa um id que não é número antes de a
  view rodar, e a view recebe um `int` pronto. Montar o endereço pelo nome
  evita escrever o mesmo caminho em vários arquivos.
- **Consequência aceita:** um endereço que não corresponde a nenhuma rota, como
  `/recado/abc/`, recebe o 404 do próprio Django, que usa o template `404.html`
  só com `DEBUG = False`. Com `DEBUG` ligado, aparece a página de depuração.

### D4. nginx com Gunicorn ou Apache com mod_wsgi

- **Decisão:** o projeto roda atrás de um servidor web de verdade. A pasta
  `servidor/` traz a configuração das duas opções: `nginx.conf` com
  `mini-mural.service`, em que o nginx repassa os pedidos ao Gunicorn, e
  `apache.conf`, em que o Apache roda o Django pelo mod_wsgi.
- **Alternativa descartada:** o servidor de desenvolvimento do Django
  (`python manage.py runserver`).
- **Motivo:** a documentação do Django diz que o `runserver` não passou por
  auditoria de segurança nem por teste de desempenho e não deve ser usado em
  produção. Com nginx ou Apache, o aluno vê a divisão que existe em qualquer
  implantação: o servidor web recebe a conexão e entrega os arquivos estáticos,
  e o Python só executa as views.
- **Consequência aceita:** rodar o projeto exige instalar e configurar um
  servidor web. O código Python só é relido quando o Gunicorn ou o Apache
  reiniciam, então cada mudança em um `.py` pede um reinício. Para ver um erro,
  o aluno abre o log do servidor.

### D5. Projeto Django mínimo

> **Revista na etapa 3 (D23):** entraram `auth`, `sessions` e `contenttypes`,
> com as tabelas deles criadas pelo `migrate`. Admin e messages continuam fora.

- **Decisão:** `INSTALLED_APPS` tem só `django.contrib.staticfiles` e `mural`.
  O `MIDDLEWARE` mantém segurança, CSRF e proteção contra clickjacking.
- **Alternativa descartada:** o projeto padrão do `startproject`, com admin,
  autenticação, sessões e mensagens.
- **Motivo:** o mural não tem login, e esses apps exigem tabelas que só o
  `migrate` cria. Sem eles, o banco tem uma única tabela, a do mural.
- **Consequência aceita:** não há painel `/admin/` para ver ou corrigir os
  recados; isso se faz no `psql`. Acrescentar login depois exige devolver
  `auth` e `sessions` e passar a usar migrations para as tabelas deles.

### D6. Consultas reunidas em `mural/recados.py`

- **Decisão:** as views chamam `listar_recados()`, `buscar_recado()`,
  `publicar_recado()` e `arquivar_recado()`. Só esse arquivo usa
  `Recado.objects`.
- **Alternativa descartada:** chamar o ORM direto nas views, ou criar um
  `Manager` próprio no modelo.
- **Motivo:** cada operação do mural ganha um nome, e quem lê a view sabe o que
  acontece sem conhecer a sintaxe de consultas do ORM.
- **Consequência aceita:** uma camada a mais para ler. Nada impede uma view de
  chamar `Recado.objects` direto; a separação depende de disciplina.

### D7. Validação em função própria, sem `django.forms`

> **Escopo na etapa 3 (D24):** vale para o formulário de recado. Login e
> cadastro usam os formulários do Django, que trazem as regras de senha.

- **Decisão:** `validar_recado()`, em `mural/validacao.py`, recebe o texto e
  devolve a mensagem de erro ou `None`. O template escreve o formulário em HTML.
- **Alternativa descartada:** uma classe `Form` com `clean_texto()`, que
  validaria o campo e desenharia o HTML.
- **Motivo:** a regra fica em uma função curta, testável sem pedido, com as
  mesmas mensagens que o JavaScript repete. O HTML do formulário, com os
  atributos de acessibilidade, fica todo visível no template.
- **Consequência aceita:** o projeto não usa o que o `Form` oferece, como
  conversão de tipos, lista de erros por campo e HTML gerado. Um campo novo
  exige ler `request.POST` e validar à mão.

## Dados

### D8. Esquema em SQL executado à mão, modelo com `managed = False`

> **Revista na etapa 3 (D23 e D26):** a tabela `recados` continua no
> `schema.sql`, mas agora aponta para `auth_user` e é carregada pelo comando
> `carregar_esquema`, depois do `migrate`.

- **Decisão:** `sql/schema.sql` apaga e cria a tabela; `sql/seed.sql` insere os
  exemplos. O modelo `Recado` usa a tabela pronta, com `managed = False`.
- **Alternativa descartada:** as migrations do Django (`makemigrations` e
  `migrate`), que criariam a tabela a partir do modelo.
- **Motivo:** o arquivo SQL é o próprio esquema, legível de cima a baixo, com
  as restrições `CHECK` à vista, e o aluno pratica o `psql`.
- **Consequência aceita:** modelo e `schema.sql` mudam juntos, à mão, e nada
  avisa se divergirem. Rodar o `schema.sql` de novo apaga os recados. O banco
  de teste que o Django cria não teria a tabela, por isso os testes usam só
  `SimpleTestCase`, sem banco.

### D9. Usuário próprio no PostgreSQL

- **Decisão:** a aplicação conecta com o usuário `mini_mural`, dono do banco
  `mini_mural`, com senha.
- **Alternativa descartada:** conectar com o superusuário `postgres` ou com o
  usuário do sistema operacional.
- **Motivo:** o Gunicorn e o Apache rodam como o usuário do servidor web, que
  não existe no PostgreSQL. Um usuário próprio funciona igual em qualquer
  máquina, e um defeito na aplicação fica restrito ao banco dela, sem alcançar
  os outros bancos do servidor.
- **Consequência aceita:** a instalação ganha um passo, criar o usuário e
  escolher a senha, e a senha fica escrita no `config.py`. Por isso o
  `config.py` fica fora do Git.

### D10. Recados no banco, compartilhados por todos

> **Revista na etapa 3 (D25):** os recados agora são compartilhados entre os
> usuários logados, e cada recado guarda o autor.

- **Decisão:** os recados ficam na tabela `recados` do PostgreSQL.
- **Alternativa descartada:** guardar os recados na sessão do Django ou em um
  arquivo JSON no servidor.
- **Motivo:** na sessão, cada navegador veria só os próprios recados. No arquivo
  JSON, dois pedidos ao mesmo tempo podem gravar por cima um do outro, e o
  Python teria de ordenar e filtrar a lista sozinho. O banco resolve a
  concorrência e faz a ordenação.
- **Consequência aceita:** dois navegadores veem o mesmo mural, e arquivar em um
  aparece no outro após recarregar. Não há dono do recado: qualquer pessoa
  arquiva qualquer recado.

### D11. Ordem do mural em cookie

> **Mantida na etapa 3:** com login, a ordem poderia ir para o banco, por
> usuário. Ela continua no cookie para não mudar o comportamento da etapa 2.

- **Decisão:** a preferência de ordem fica no cookie `mini_mural_ordem`.
- **Alternativa descartada:** uma tabela `preferencias` no banco.
- **Motivo:** a ordem é uma escolha de quem usa o navegador. Sem login, o
  servidor não sabe quem é quem, e uma linha no banco seria a mesma ordem para
  todo mundo.
- **Consequência aceita:** a ordem não acompanha a pessoa em outro navegador e
  some se ela limpar os cookies. Valor desconhecido no cookie vira a ordem
  padrão, mais recentes primeiro.

### D12. Status como texto com `CHECK`

- **Decisão:** `status text CHECK (status IN ('publicado', 'arquivado'))` na
  tabela, e as constantes `Recado.PUBLICADO` e `Recado.ARQUIVADO` no modelo.
- **Alternativa descartada:** tipo enumerado do PostgreSQL (`CREATE TYPE ...
  AS ENUM`) ou uma coluna booleana `arquivado`.
- **Motivo:** o `CHECK` mostra os valores válidos na própria definição da
  tabela, e o valor gravado é a palavra que aparece na tela.
- **Consequência aceita:** cada linha repete o texto do status. Um terceiro
  status exige alterar a restrição, o que, sem migrations, significa recriar a
  tabela (D8), e acrescentar a constante no modelo.

### D13. Id gerado pelo banco

- **Decisão:** `id bigint GENERATED ALWAYS AS IDENTITY` na tabela e
  `BigAutoField` no modelo.
- **Alternativa descartada:** UUID gerado no Python.
- **Motivo:** o banco garante id único mesmo com dois pedidos ao mesmo tempo, e
  o endereço do detalhe fica curto (`/recado/4/`).
- **Consequência aceita:** os ids são sequenciais e revelam quantos recados já
  foram criados. Recriar a tabela com o `schema.sql` recomeça a contagem em 1.

### D14. Hora em `timestamptz`, com `USE_TZ`

- **Decisão:** o banco guarda o instante com fuso (`timestamptz`). Com
  `USE_TZ = True`, o Django lê o valor como data com fuso e o filtro `date` dos
  templates mostra a hora em `TIME_ZONE`, `America/Araguaina`.
- **Alternativa descartada:** `timestamp` sem fuso e `USE_TZ = False`, com a
  hora local gravada direto.
- **Motivo:** com fuso guardado, a hora exibida não depende do fuso da conexão
  nem do servidor; basta trocar `FUSO_HORARIO` no `config.py`.
- **Consequência aceita:** gravar uma data criada com `datetime.now()`, sem
  fuso, gera aviso do Django; o certo é `django.utils.timezone.now()`. O nome do mês em pt-br vem com inicial
  maiúscula ("Março"), e o template usa o filtro `lower`.

## Comportamento

### D15. Regra de negócio no Python, repetida no navegador só como aviso

- **Decisão:** `validar_recado()` decide se o recado é gravado. O `mural.js`
  repete a conferência para avisar antes do envio, e o banco tem restrições
  `CHECK` como última barreira.
- **Alternativa descartada:** validar só no navegador, com `required` e
  `maxlength`, ou só no servidor, sem JavaScript.
- **Motivo:** o navegador está sob controle de quem usa; um `curl` envia o que
  quiser. O aviso no navegador poupa um pedido ao servidor: a mensagem aparece
  abaixo do campo, o foco volta a ele e o botão continua habilitado.
- **Consequência aceita:** a regra e as mensagens existem em Python e em
  JavaScript. Mudar o limite exige alterar `LIMITE_DO_RECADO`, que já alimenta o
  `data-limite` do formulário, e as mensagens nos dois arquivos.

### D16. POST/redirect/GET em toda gravação

- **Decisão:** depois de gravar, a view responde 303 e o navegador faz um GET.
  A função `redirecionar()` troca o 302 do Django por 303.
- **Alternativa descartada:** devolver o HTML da página logo depois do POST.
- **Motivo:** recarregar a página depois de um POST pede ao navegador para
  reenviar o formulário, e o recado seria gravado duas vezes.
- **Consequência aceita:** cada gravação custa dois pedidos. Uma mensagem de
  sucesso precisa ir no endereço (`?salvo=1`), porque o GET seguinte não sabe o
  que aconteceu no POST.

### D17. Texto inválido responde 422 com a página inteira

- **Decisão:** com erro de validação, a mesma página é desenhada de novo com o
  código 422, a mensagem e o texto digitado.
- **Alternativa descartada:** redirecionar de volta com a mensagem guardada no
  framework de mensagens do Django (`django.contrib.messages`).
- **Motivo:** o framework de mensagens exigiria acrescentar um app e um
  middleware, com a mensagem guardada em sessão ou em cookie, e o projeto ficou
  mínimo de propósito (D5). O código 422 diz, a quem lê a resposta, que o
  pedido foi recusado.
- **Consequência aceita:** depois de um erro, o endereço mostra o POST; se a
  pessoa recarregar, o navegador pergunta se deve reenviar o formulário.

### D18. Arquivar é repetível

- **Decisão:** a consulta de arquivar filtra `status='publicado'`. Arquivar
  duas vezes, ou arquivar um id que não existe, não altera nada e redireciona
  normalmente.
- **Alternativa descartada:** buscar o recado antes e responder 404 ou 409
  quando ele já está arquivado ou não existe.
- **Motivo:** dois cliques seguidos no botão, ou um botão em uma aba antiga,
  levam ao mesmo resultado sem página de erro.
- **Consequência aceita:** quem arquiva um id inexistente pela lista não recebe
  aviso. Pelo detalhe, o redirecionamento cai na página "não encontrado".

### D19. Proteção CSRF ligada

- **Decisão:** o `CsrfViewMiddleware` fica ligado e todo formulário leva
  `{% csrf_token %}`.
- **Alternativa descartada:** desligar a proteção, já que sem login um
  formulário forjado só consegue publicar ou arquivar um recado.
- **Motivo:** no Django a proteção vem pronta e custa uma linha por formulário.
  O token fica em cookie, sem precisar de sessão. Desligar exigiria mexer no
  `MIDDLEWARE` e ensinaria o caminho errado para quando houver login.
- **Consequência aceita:** um POST sem o token recebe 403. Testar com `curl`
  exige ler o cookie `csrftoken` primeiro, como mostra o README.

## Configuração

### D20. Configuração local em `config.py`

- **Decisão:** `settings.py` lê de `config.py` a `SECRET_KEY`, o `DEBUG`, os
  endereços aceitos, o banco e o fuso. O `config.exemplo.py` é o modelo.
- **Alternativa descartada:** variáveis de ambiente, lidas com `os.environ` ou
  com uma biblioteca como `django-environ`.
- **Motivo:** um arquivo Python com comentários é mais fácil de ler e de editar
  do que variáveis espalhadas pelo terminal, pela unidade do systemd e pela
  configuração do Apache.
- **Consequência aceita:** a senha do banco e a `SECRET_KEY` ficam em um
  arquivo na pasta do projeto, que precisa ficar fora do Git e legível só por
  quem roda a aplicação.

### D21. Arquivos estáticos entregues pelo servidor web

- **Decisão:** o `collectstatic` copia CSS e JavaScript para `staticfiles/`, e
  o nginx ou o Apache entregam essa pasta em `/static/`, sem passar pelo Django.
- **Alternativa descartada:** o Django entregar os estáticos, com a biblioteca
  WhiteNoise ou com a view de desenvolvimento do `staticfiles`.
- **Motivo:** é o modelo que a documentação do Django descreve para produção, e
  o servidor web entrega arquivos do disco sem ocupar um processo Python.
- **Consequência aceita:** depois de mudar um CSS ou um JavaScript, é preciso
  rodar o `collectstatic` de novo. Sem isso, o navegador continua recebendo a
  versão anterior.

## Ambiente de desenvolvimento

### D22. Docker com três serviços: nginx, aplicação e banco

> **Revista na etapa 3 (D26):** o PostgreSQL deixou de executar o `schema.sql`
> na primeira partida. Quem cria as tabelas agora é o contêiner `app`.

- **Decisão:** `compose.yaml` sobe três contêineres. O `web` usa a imagem
  oficial do nginx e entrega os estáticos; o `app` roda o Django no Gunicorn,
  em uma imagem feita a partir de `python:3.13-slim`; o `banco` usa a imagem
  oficial `postgres:18`, que executa o `schema.sql` e o `seed.sql` na primeira
  partida. Os estáticos passam do `app` para o `web` pelo volume `estaticos`.
- **Alternativa descartada:** dois contêineres, com o Django entregando os
  próprios estáticos pela biblioteca WhiteNoise, ou com o `runserver`.
- **Motivo:** o Gunicorn não entrega arquivos estáticos, e o projeto deixa essa
  tarefa para o servidor web (D21). Com nginx na frente, o Docker reproduz a
  mesma divisão da instalação direta com nginx e Gunicorn (D4), sem mudar o
  código. A imagem do PostgreSQL já sabe executar arquivos SQL na primeira
  partida, então o esquema continua sendo o mesmo `schema.sql` (D8).
- **Consequência aceita:** o contêiner usa `docker/config.py`, que lê a chave e
  o banco das variáveis de ambiente, no lugar do `config.py` local; os dois arquivos
  precisam continuar com as mesmas variáveis. O `app` roda o `collectstatic` a
  cada partida, para o volume acompanhar a imagem. A imagem guarda uma cópia do
  código, então cada mudança pede `docker compose up --build`. O `schema.sql` só
  roda com o volume vazio, e mudar o esquema exige `docker compose down -v`, que
  apaga os recados. A senha e a `SECRET_KEY` ficam escritas em `compose.yaml`,
  o que serve para a máquina de desenvolvimento e não para produção.

## Login (etapa 3)

### D23. Login com `django.contrib.auth` e migrations só para os apps do Django

- **Decisão:** o login usa o `django.contrib.auth`, com as sessões do
  `django.contrib.sessions` guardadas no banco. As tabelas desses apps
  (`auth_user`, `django_session` e outras) vêm do `python manage.py migrate`. A
  tabela do mural continua no `schema.sql`, com `managed = False` (D8).
- **Alternativa descartada:** uma tabela de usuários própria no `schema.sql`,
  com hash de senha e sessão escritos à mão, como seria sem framework.
- **Motivo:** o Django já resolve o login com cuidado: hash de senha com PBKDF2,
  troca do identificador de sessão no login, regras de senha e proteção do
  parâmetro `next`. Escrever tudo à mão ensinaria a reinventar, com mais chance
  de defeito, o que o framework entrega pronto. A consequência de D5 já previa
  este caminho.
- **Consequência aceita:** o banco passa a ter tabelas de duas origens, e a
  ordem importa: primeiro o `migrate`, depois o `schema.sql`, porque `recados`
  aponta para `auth_user`. O tipo de `autor_id` precisa acompanhar o de
  `auth_user.id`, que é `integer`. A consulta de recados com `select_related`
  traz para a memória também o hash da senha do autor, que o template não usa.

### D24. Telas de login, saída e cadastro com as views e os formulários do Django

- **Decisão:** a tela de entrar é a `LoginView`, com um template próprio e
  resposta 422 quando o login falha. A saída é a `LogoutView`, que só aceita
  POST. O cadastro é uma view em função com o `UserCreationForm`, que cria o
  usuário e já faz o login.
- **Alternativa descartada:** escrever as três telas à mão, lendo
  `request.POST` como no formulário de recado (D7).
- **Motivo:** os formulários do Django aplicam as regras de
  `AUTH_PASSWORD_VALIDATORS`, conferem nome repetido sem diferenciar maiúsculas
  e escrevem as mensagens em português. Repetir isso à mão duplicaria código
  sensível.
- **Consequência aceita:** o HTML dos campos sai dos widgets do Django, e o
  template só o posiciona. O login diferencia maiúsculas no nome, enquanto o
  cadastro recusa nomes que só diferem nelas; a conta `exemplo` não entra como
  `Exemplo`, e a mensagem de erro do Django avisa isso.

### D25. Tudo exige login, menos o recado público

- **Decisão:** mural, Sobre, publicar e arquivar levam `@login_required`, que
  manda quem não entrou para `/entrar/?next=...`. A exceção é o detalhe de um
  recado marcado como público, que qualquer pessoa lê pelo endereço, sem botão
  de arquivar. Todo recado nasce privado (`publico boolean DEFAULT false`), e a
  caixa "Público" só existe no formulário de publicação. O recado guarda o
  autor. Qualquer usuário logado arquiva qualquer recado, como na etapa 2.
- **Alternativa descartada:** mostrar a quem não entrou uma lista dos recados
  públicos em `/`, ou deixar só o autor arquivar o próprio recado.
- **Motivo:** o pedido da etapa é que todo o mural exija login e que o recado
  público possa ser lido sem login. O detalhe por endereço atende a leitura
  pública com a menor mudança, e arquivar continua com a regra da etapa 2.
- **Consequência aceita:** quem não entrou só chega a um recado público se
  receber o endereço dele. Um recado não muda de privado para público depois de
  publicado. Um usuário com recados não pode ser apagado (`on_delete=PROTECT` e
  o `REFERENCES` da tabela). Não há limite de tentativas de login: alguém pode
  testar senhas à vontade, o que um sistema em produção precisaria impedir.

### D26. Esquema carregado pelo comando `carregar_esquema`

- **Decisão:** o comando `python manage.py carregar_esquema`, em
  `mural/management/commands/`, executa o `schema.sql` e, com `--exemplos`, cria
  o usuário `exemplo` pelo ORM e executa o `seed.sql`. Com `--se-ausente`, ele
  não faz nada se a tabela `recados` já existe. No Docker, o contêiner `app` roda
  `migrate` e `carregar_esquema --se-ausente --exemplos` a cada partida.
- **Alternativa descartada:** continuar com o `psql -f`, na instalação direta, e
  com o `/docker-entrypoint-initdb.d` do PostgreSQL, no Docker.
- **Motivo:** o `schema.sql` agora depende das tabelas do `migrate`, e o
  PostgreSQL executaria os arquivos de `initdb` antes de o Django criar essas
  tabelas. O comando roda no lugar certo da sequência, nos dois jeitos de
  instalar, e cria o usuário de exemplo com o hash certo sem escrevê-lo no SQL.
- **Consequência aceita:** o projeto tem um comando próprio para manter. Sem
  `--se-ausente`, ele apaga os recados, como o `schema.sql` sempre fez; no
  Docker, uma mudança no esquema só vale depois de `docker compose down -v`.
