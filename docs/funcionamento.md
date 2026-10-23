# Como a aplicação funciona

Este documento descreve o que a aplicação faz e o caminho de cada pedido, do
navegador ao banco e de volta. As escolhas por trás desse caminho estão em
[decisoes.md](decisoes.md).

## As quatro partes

A aplicação tem quatro partes, e cada uma tem uma responsabilidade.

| Parte | Onde roda | Responsabilidade |
|---|---|---|
| Navegador | Na máquina de quem usa | Mostra o HTML, aplica o CSS e roda o `mural.js`, que avisa erros do formulário antes do envio |
| Servidor web (nginx ou Apache) | No servidor | Recebe a conexão, entrega direto os arquivos de `/static/` e passa os outros pedidos ao Django |
| Django (no Gunicorn ou no mod_wsgi) | No servidor, em processos Python | Executa a view do endereço pedido: aplica as regras, consulta o banco e monta o HTML da resposta |
| PostgreSQL | No servidor de banco, que pode ser a mesma máquina | Guarda usuários, sessões e recados, e recusa dados que quebram as restrições das tabelas |

Com nginx, o Django roda no Gunicorn, um processo separado que escuta em
`127.0.0.1:8000`, e o nginx repassa os pedidos a ele por HTTP. Com Apache, o
mod_wsgi cria os processos Python e os administra de dentro do próprio Apache.
Nos dois casos, a porta de entrada do Django é a `application` de
`mini_mural/wsgi.py`, e o código do projeto é o mesmo.

O navegador nunca fala com o banco. Todo acesso a dados passa pelo Django, e é
nele que mora a regra de negócio: só quem entrou publica e arquiva, o texto do
recado tem de 1 a 280 caracteres, todo recado nasce publicado e privado, e só
um recado publicado pode ser arquivado.

## Funcionalidades

São seis funcionalidades: criar conta e entrar, publicar, listar, abrir o
detalhe, arquivar e escolher a ordem do mural. Todas exigem login, menos a
leitura de um recado público.

```mermaid
flowchart LR
    V(["Visitante sem login"])
    U(["Usuário logado"])

    subgraph conta ["Conta"]
        C1["Criar conta: /cadastro/"]
        C2["Entrar: /entrar/"]
        C3["Sair: /sair/"]
    end

    subgraph mural ["Mural: /"]
        F1["Publicar recado"]
        F2["Ver a lista de recados"]
        F3["Ver o resumo: publicados e arquivados"]
        F4["Arquivar recado pela lista"]
    end

    subgraph detalhe ["Detalhe: /recado/N/"]
        F5["Ver o texto completo, data e hora"]
        F6["Arquivar recado pelo detalhe"]
        F7["Ver aviso de recado não encontrado"]
    end

    subgraph sobre ["Sobre: /sobre/"]
        F8["Ler a descrição do projeto"]
        F9["Escolher a ordem do mural"]
    end

    V --> C1
    V --> C2
    V -. "só recado público, sem arquivar" .-> F5
    C1 -. "já entra na conta" .-> U
    C2 --> U
    U --> C3
    U --> F1
    U --> F2
    U --> F4
    U --> F5
    U --> F6
    U --> F9
    F2 --> F3
    F2 -- "clique no texto" --> F5
    F5 -. "id inexistente" .-> F7
    F9 -. "muda a ordem de" .-> F2
    U --> F8
```

## Endereços

O arquivo `mural/urls.py` liga cada endereço a uma view de `mural/views.py`.

| Endereço | Método | Login | View | O que faz | Resposta |
|---|---|---|---|---|---|
| `/` | GET | Sim | `mural` | Mostra o formulário, o resumo e a lista na ordem do cookie | 200 com HTML |
| `/` | POST | Sim | `mural` | Valida e grava um recado novo, público ou privado | 303 para `/` se válido, 422 com a página e a mensagem se inválido |
| `/recado/N/` | GET | Só para recado privado | `recado` | Mostra um recado | 200, ou 404 se o recado não existe |
| `/recado/N/arquivar/` | POST | Sim | `arquivar` | Arquiva o recado `N` | 303 para a lista ou para o detalhe; 405 se chegar por GET |
| `/sobre/` | GET e POST | Sim | `sobre` | Mostra e grava a ordem no cookie | 200; 303 para `/sobre/?salvo=1` depois de gravar |
| `/entrar/` | GET e POST | Não | `Entrar` (`LoginView`) | Mostra o formulário e confere usuário e senha | 302 para `next` ou `/` se conferem, 422 se não |
| `/cadastro/` | GET e POST | Não | `cadastro` | Cria a conta e já entra nela | 303 para `/` se criou, 422 com as mensagens se não |
| `/sair/` | POST | Sim | `LogoutView` | Apaga a sessão | 302 para `/entrar/`; 405 se chegar por GET |

Uma view com `@login_required` responde 302 para `/entrar/?next=` seguido do
endereço pedido, e o login devolve a pessoa a esse endereço.

Um endereço sem rota, como `/recado/abc/` ou `/qualquer-coisa`, recebe 404 do
próprio Django, com o template `404.html`. Todo POST sem o token CSRF recebe
403, e um pedido com nome de site fora de `ENDERECOS_ACEITOS` recebe 400.

## O caminho de um pedido dentro do Django

Antes de chegar à view, o pedido passa pelos middlewares de `settings.py`. O de
sessão lê o cookie `sessionid` e carrega a sessão do banco, o de CSRF confere o
token dos POST, e o de autenticação preenche `request.user` com o usuário
logado, ou com um usuário anônimo. O Django então procura o
endereço em `urls.py` e chama a view. A view usa as funções de `recados.py`,
`validacao.py` e `preferencias.py` e termina com `render()`, que monta o HTML a
partir de um template, ou com `redirecionar()`.

```mermaid
flowchart LR
    pedido(["Pedido"]) --> mw["Middlewares: segurança, sessão, CSRF, autenticação"]
    mw --> login{"A view exige login?"}
    login -- "sim, e não há usuário" --> entrar(["302 para /entrar/"])
    login -- "não, ou há usuário" --> urls
    urls["mural/urls.py"]
    urls --> view["View em mural/views.py"]
    view --> funcoes["recados.py, validacao.py, preferencias.py"]
    funcoes --> orm["Modelo Recado (ORM)"]
    orm --> pg[("PostgreSQL")]
    view --> tpl["Template em mural/templates/"]
    tpl --> resposta(["Resposta HTML"])
    view -. "depois de gravar" .-> redir(["Resposta 303"])
```

### Abrir o mural

O primeiro diagrama mostra o servidor web separado do Django. Os pedidos de
página passam pelos dois; os de CSS e JavaScript param no servidor web, que lê
o arquivo de `staticfiles/` sem acionar o Python.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant N as Navegador
    participant S as nginx ou Apache
    participant D as Django: views.mural
    participant B as PostgreSQL

    U->>N: abre http://localhost:8081/, já logado
    N->>S: GET / com os cookies sessionid e mini_mural_ordem
    S->>D: repassa o pedido
    D->>D: middlewares carregam a sessão, e o login_required encontra request.user
    D->>D: ler_ordem() escolhe a ordenação
    D->>B: SELECT ... FROM recados ORDER BY criado_em DESC, id DESC
    B-->>D: linhas da tabela recados
    D->>D: resumir_recados() e render() do template
    D-->>S: HTML da página e cookie csrftoken
    S-->>N: 200 com o HTML
    N->>S: GET /static/mural/css/estilo.css e /static/mural/js/mural.js
    S-->>N: arquivos lidos de staticfiles/, sem passar pelo Django
    N-->>U: mural desenhado
```

Os diagramas seguintes juntam servidor web e Django em um participante só, para
destacar o que o código do projeto faz.

### Publicar um recado válido

Depois de gravar, a view responde 303 sem HTML, e o navegador faz um GET novo.
Esse padrão se chama **POST/redirect/GET**. Como o último pedido da página foi
um GET, recarregar depois de publicar repete só a leitura, e o recado é gravado
uma vez.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant N as Navegador e mural.js
    participant D as Django: views.mural
    participant B as PostgreSQL

    U->>N: digita o texto e clica em Publicar
    N->>N: mural.js valida e deixa o envio seguir
    N->>D: POST / com texto e csrfmiddlewaretoken
    D->>D: middleware confere o token CSRF
    D->>D: normalizar_quebras_de_linha() e validar_recado()
    D->>B: INSERT INTO recados (texto, criado_em, status) VALUES (..., DEFAULT, DEFAULT)
    B-->>D: id, criado_em e status do recado novo
    D-->>N: 303 See Other, Location: /
    N->>D: GET /
    D->>B: SELECT ... ORDER BY criado_em
    B-->>D: linhas, já com o recado novo
    D-->>N: 200 com o HTML atualizado
```

### Publicar um texto inválido

O texto inválido pode ser barrado em dois lugares. Com JavaScript ligado, o
`mural.js` cancela o envio, mostra a mensagem e devolve o foco ao campo; nenhum
pedido sai do navegador. Sem JavaScript, ou com um pedido montado à mão, a view
faz a mesma conferência e responde 422 com o formulário preenchido. Nos dois
casos o banco não recebe nada.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant N as Navegador e mural.js
    participant D as Django: views.mural
    participant B as PostgreSQL

    U->>N: clica em Publicar com o campo vazio
    alt JavaScript ligado
        N->>N: validar() devolve a mensagem
        N-->>U: mensagem abaixo do campo e foco no campo
    else JavaScript desligado ou pedido feito à mão
        N->>D: POST / com texto vazio
        D->>D: validar_recado() devolve a mensagem
        D->>B: SELECT para desenhar a lista
        B-->>D: linhas
        D-->>N: 422 com a página, a mensagem e o texto digitado
    end
```

### Arquivar um recado

O botão "Arquivar" é um formulário que envia POST para `/recado/N/arquivar/`.
Arquivar muda dados, por isso usa POST: um link comum seria um GET, e um GET
pode ser disparado por um buscador ou por uma pré-carga do navegador. O
decorador `@require_POST` responde 405 a qualquer outro método.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant N as Navegador
    participant D as Django: views.arquivar
    participant B as PostgreSQL

    U->>N: clica em Arquivar
    N->>D: POST /recado/4/arquivar/ com o token CSRF
    D->>B: UPDATE recados SET status = arquivado WHERE id = 4 AND status = publicado
    B-->>D: 1 linha alterada, ou 0 se já estava arquivado
    alt veio da lista
        D-->>N: 303, Location: / com a âncora do recado
    else veio do detalhe (voltar_para=detalhe)
        D-->>N: 303, Location: /recado/4/
    end
    N->>D: GET da página de destino
    D-->>N: 200 com o recado marcado como Arquivado
```

### Escolher a ordem do mural

A ordem é a única informação que fica no navegador. A view grava um cookie, e o
navegador o devolve em todo pedido seguinte. A view `sobre` nem consulta o
banco.

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant N as Navegador
    participant D as Django: views.sobre

    U->>N: marca Mais antigos primeiro e clica em Salvar ordem
    N->>D: POST /sobre/ com ordem=mais-antigos
    D->>D: ordem_valida() confere a lista fechada ORDENS
    D-->>N: 303, Set-Cookie: mini_mural_ordem=mais-antigos
    N->>D: GET /sobre/?salvo=1 com o cookie
    D-->>N: 200 com Preferência salva
    Note over N,D: Daqui em diante, todo GET / leva o cookie, e a lista vem em ordem crescente
```

## Login e acesso

O login usa o `django.contrib.auth` e as sessões do Django. No login, o Django
grava o id do usuário na sessão, guardada na tabela `django_session`, e o
navegador recebe só o identificador da sessão, no cookie `sessionid`. Em cada
pedido seguinte, os middlewares leem o cookie, carregam a sessão e preenchem
`request.user`.

### Entrar

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant N as Navegador
    participant D as Django: LoginView
    participant B as PostgreSQL

    U->>N: abre http://localhost:8081/
    N->>D: GET / sem cookie de sessão
    D-->>N: 302, Location: /entrar/?next=/
    N->>D: GET /entrar/?next=/
    D-->>N: 200 com o formulário e o cookie csrftoken
    U->>N: digita usuário e senha e clica em Entrar
    N->>D: POST /entrar/ com username, password, next e o token
    D->>D: middleware confere o token CSRF
    D->>B: SELECT ... FROM auth_user WHERE username = ...
    B-->>D: a linha do usuário, com o hash PBKDF2
    D->>D: confere a senha com o hash
    alt usuário e senha conferem
        D->>B: grava a sessão nova em django_session
        D-->>N: 302 para next, cookie sessionid novo e token CSRF novo
    else não conferem
        D-->>N: 422 com a mensagem do Django
    end
```

No login, o Django troca o identificador da sessão e o token CSRF. A troca
protege contra a **fixação de sessão**: se alguém conseguisse plantar um
identificador no navegador da vítima antes do login, esse identificador deixa
de valer quando ela entra. O parâmetro `next` só é seguido se apontar para o
próprio site.

### Criar conta

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant N as Navegador
    participant D as Django: views.cadastro
    participant B as PostgreSQL

    U->>N: preenche usuário, senha e confirmação
    N->>D: POST /cadastro/ com username, password1, password2 e o token
    D->>D: UserCreationForm valida os campos e as regras de senha
    D->>B: SELECT 1 FROM auth_user WHERE UPPER(username) = UPPER(...)
    alt algum campo inválido ou nome já existe
        D-->>N: 422 com a mensagem embaixo de cada campo
    else campos válidos
        D->>B: INSERT INTO auth_user (... password = hash PBKDF2 ...)
        D->>D: login() com o usuário novo
        D-->>N: 303, Location: /
    end
```

### Recado público e recado privado sem login

```mermaid
sequenceDiagram
    autonumber
    actor V as Visitante sem login
    participant N as Navegador
    participant D as Django: views.recado
    participant B as PostgreSQL

    V->>N: abre o endereço de um recado
    N->>D: GET /recado/N/
    D->>B: SELECT ... FROM recados INNER JOIN auth_user WHERE recados.id = N
    B-->>D: o recado, com publico e autor
    alt recado público
        D-->>N: 200 com o recado, sem o botão de arquivar
    else recado privado
        D-->>N: 302, Location: /entrar/?next=/recado/N/
    end
```

## Validação em três camadas

A regra do texto do recado aparece em três lugares, com papéis diferentes.

| Camada | Onde | Papel |
|---|---|---|
| Navegador | `maxlength` no `<textarea>` e `validar()` em `mural/static/mural/js/mural.js` | Conforto: avisa antes do envio e impede digitar além do limite |
| Django | `validar_recado()` em `mural/validacao.py` | Regra que vale: decide se o recado é gravado e qual mensagem a pessoa vê |
| Banco | restrições `CHECK` em `sql/schema.sql` | Última barreira: recusa a gravação se um defeito no código deixar passar um texto inválido |

O navegador não é confiável como barreira, porque qualquer pessoa pode enviar um
POST com `curl` sem passar pelo formulário. Por isso o Django repete a
conferência.

Um detalhe de contagem: o navegador envia cada quebra de linha do `<textarea>`
como `\r\n`, dois caracteres, mas o `maxlength` conta como um. A função
`normalizar_quebras_de_linha()` troca `\r\n` por `\n` antes de validar, e assim
o Python conta igual ao navegador. O `len()` do Python conta caracteres, e cada
letra acentuada conta uma vez, mesmo ocupando dois bytes em UTF-8.

## Cuidados de segurança

A tabela liga cada risco ao cuidado que o evita e ao lugar onde ele está.

| Risco | Cuidado | Onde |
|---|---|---|
| Injeção de SQL | O ORM manda todo valor como parâmetro; a ordem escolhe entre dois `order_by` fixos | `mural/recados.py` |
| Script injetado em recado (XSS) | Os templates do Django escapam toda variável por padrão; o único `safe` é no texto de ajuda da senha, que o próprio Django monta | `mural/templates/` |
| Formulário enviado por outro site (CSRF) | `CsrfViewMiddleware` e `{% csrf_token %}` em todo formulário | `settings.py` e templates |
| Redirecionamento para site externo | O destino depois de arquivar sai de duas opções fixas, nunca do pedido | `views.arquivar` |
| Mudança de dados por link | Publicar e salvar a ordem só gravam em POST; arquivar tem `@require_POST`, e a `LogoutView` só aceita POST | `mural/views.py` e `mural/urls.py` |
| Senha vazada do banco | `auth_user` guarda só o hash PBKDF2, com sal | `django.contrib.auth` |
| Fixação de sessão | O login troca o identificador da sessão | `django.contrib.auth` |
| Redirecionamento externo depois do login | A `LoginView` só segue um `next` do próprio site | `views.Entrar` |
| Senha fraca | Regras de `AUTH_PASSWORD_VALIDATORS`: tamanho mínimo, senha comum, só números, parecida com o nome | `settings.py` |
| Cabeçalho `Host` forjado | `ALLOWED_HOSTS` recusa nomes fora da lista com 400 | `config.py` |

Um risco ficou sem cuidado: não há limite de tentativas de login, e alguém
pode testar senhas à vontade. A decisão D25, em [decisoes.md](decisoes.md),
registra essa consequência.

## Com Docker

O `compose.yaml` monta as mesmas partes em contêineres. O `web` faz o papel do
servidor web, o `app` roda o Django no Gunicorn e o `banco` roda o PostgreSQL.
O navegador continua falando só com o nginx, pela porta 8081 da sua máquina.

```mermaid
flowchart LR
    navegador["Navegador"]

    subgraph maquina ["Sua máquina"]
        porta["localhost:8081"]
        subgraph compose ["Rede do Compose"]
            web["web: nginx, porta 80"]
            app["app: Django no Gunicorn, porta 8000"]
            banco[("banco: PostgreSQL, porta 5432")]
        end
        estaticos[("volume estaticos")]
        dados[("volume dados")]
    end

    navegador --> porta
    porta --> web
    web -- "repassa para app:8000" --> app
    web -. "lê /static/" .-> estaticos
    app -. "collectstatic grava" .-> estaticos
    app -- "host banco" --> banco
    banco --- dados
```

Dentro da rede do Compose, cada serviço é encontrado pelo próprio nome. Por
isso o `docker/nginx.conf` repassa os pedidos para `app:8000`, e o
`docker/config.py` usa `banco` como endereço do PostgreSQL. Só a porta do nginx
é publicada na sua máquina; o Gunicorn e o PostgreSQL ficam alcançáveis apenas
de dentro da rede.

Na primeira subida, com o volume `dados` vazio, a imagem do PostgreSQL cria o
usuário e o banco `mini_mural`, sem tabelas. O `app` só liga depois que o banco
responde ao `pg_isready`, conferido pelo `healthcheck` do `compose.yaml`. A
cada partida, ele roda, em ordem:

1. `migrate`, que cria ou atualiza as tabelas do `auth` e das sessões;
2. `carregar_esquema --se-ausente --exemplos`, que cria a tabela `recados`, o
   usuário `exemplo` e os recados de exemplo, só se a tabela ainda não existe;
3. `collectstatic`, que copia CSS e JavaScript para o volume `estaticos`;
4. o Gunicorn.

A tabela `recados` aponta para `auth_user`, por isso ela vem depois do
`migrate` e não pode ser criada pelo PostgreSQL na primeira partida.

## Quando algo dá errado

Uma exceção não tratada, como o banco desligado ou um SQL com defeito, faz o
Django responder 500 com o template `500.html`, sem informação interna. O
`LOGGING` de `settings.py` manda o rastro completo para a saída de erro, que
vai para o diário do systemd (`journalctl -u mini-mural`) com Gunicorn, ou para
o `mini-mural-erro.log` com Apache, ou para a saída do contêiner com Docker
(`docker compose logs app`). Se a página "Algo deu errado" aparecer,
leia o log.

O `DEBUG = True` no `config.py` troca essas páginas pela página de depuração do
Django, com o código e as variáveis. Ela ajuda a achar um defeito na sua
máquina, mas mostra detalhes internos a quem abrir o site.
