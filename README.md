# Mini Mural em Django

Mini Mural é um mural de recados, aplicação de exemplo da disciplina de
Desenvolvimento WebMobile (UFT), feita como um monólito simples:

- HTML, CSS e JavaScript básicos no navegador;
- Python e Django no servidor, usando só o essencial do framework;
- PostgreSQL como banco, com o esquema do mural em um arquivo SQL.

O mural não usa migrations; só as tabelas de usuários e sessões do próprio
Django vêm delas. Não há etapa de build de front-end. Para rodar na sua máquina
sem instalar Python, servidor web e PostgreSQL, use o
[Docker](#rodar-com-docker).

## Funcionalidades

- Criar conta, entrar e sair. Todo o mural exige login.
- Publicar um recado de até 280 caracteres, com contador e aviso de erro. O
  recado nasce privado; marcado como público, ele pode ser lido sem login, pelo
  endereço dele.
- Ver a lista de recados com hora, autor e o resumo de publicados e arquivados.
- Abrir o detalhe de um recado, com data e hora por extenso.
- Arquivar um recado pela lista ou pelo detalhe.
- Escolher, em Sobre, a ordem do mural, guardada no navegador.

Como cada uma funciona, e por quê, está em [docs/](docs/README.md).

## Etapas

O projeto evolui por etapas. Cada ramo congela o estado do código no fim de uma
etapa, e o `main` sempre aponta para a mais recente.

| Ramo | Etapa | Conteúdo |
|---|---|---|
| `etapa-1-monolito` | 1: Monólito | Mural sem login, instalado direto com nginx e Gunicorn, ou Apache e mod_wsgi, e PostgreSQL. |
| `etapa-2-docker` | 2: Docker | O mesmo mural, com um `compose.yaml` para rodar na própria máquina. |
| `etapa-3-login` | 3: Login | Cadastro, login e saída com `django.contrib.auth`; todo o mural exige login, e o recado pode ser público. |
| `main` | (a mais recente) | Igual ao ramo da etapa mais recente. |

Para estudar uma etapa, troque de ramo, por exemplo `git switch etapa-1-monolito`.

Cada etapa tem o próprio esquema de banco, e trocar de ramo não muda o banco.
Recrie o banco ao trocar de etapa, ou as páginas falham com erros como
`column recados.autor_id does not exist`. Com Docker, rode
`docker compose down -v` antes do `docker compose up --build`. Na instalação
direta, rode o `migrate` e o `carregar_esquema` da etapa nova; nas etapas 1 e
2, que não têm o comando, rode o `sql/schema.sql` com o `psql`. Nos dois casos,
os recados da etapa anterior se perdem.

## O que você precisa

- Python 3.10 ou mais novo, com o módulo `venv`.
- PostgreSQL 14 ou mais novo, com o cliente `psql`.
- Um servidor web, em uma destas duas combinações:
  - nginx com Gunicorn, em que o nginx repassa os pedidos ao Gunicorn, um
    processo Python separado que roda o Django;
  - Apache com mod_wsgi, em que o próprio Apache cria os processos Python.

As duas funcionam igual para o projeto. A pasta `servidor/` tem a configuração
pronta de cada uma, e a decisão D4, em [docs/decisoes.md](docs/decisoes.md),
explica por que o projeto usa um servidor web de verdade.

Os passos de instalação usam Debian ou Ubuntu, o sistema mais comum em
servidores e nos laboratórios. A seção [No macOS](#no-macos) traz as
diferenças.

## Rodar com Docker

O Docker sobe a aplicação em três contêineres: `web`, com o nginx; `app`, com o
Django no Gunicorn; e `banco`, com o PostgreSQL. O nginx existe porque o
Gunicorn não entrega os arquivos estáticos (decisão D21). Você precisa só do
Docker com o Compose (Docker Desktop, ou Docker Engine com o plugin
`compose`).

Na pasta do projeto:

```bash
docker compose up --build
```

Quando o terminal mostrar o Gunicorn pronto, abra <http://localhost:8081>. Na
primeira vez, o contêiner `app` roda o `migrate` e o `carregar_esquema`, que
cria a tabela do mural, o usuário de exemplo e os recados de exemplo. Entre com
o usuário `exemplo`, senha `senha-de-exemplo`, ou crie uma conta.

O terminal fica preso mostrando os logs dos três contêineres, inclusive os
erros do Django. Para parar, use Ctrl+C. Os comandos abaixo rodam em outro
terminal, na mesma pasta.

Para rodar os testes dentro do contêiner da aplicação:

```bash
docker compose exec app python manage.py test
```

Para desligar e remover os contêineres, mantendo usuários e recados:

```bash
docker compose down
```

Para apagar também os dados e voltar aos exemplos na próxima subida:

```bash
docker compose down -v
```

Três detalhes mudam em relação à instalação direta:

- **Configuração:** o contêiner usa `docker/config.py`, que lê a `SECRET_KEY` e
  os dados do banco das variáveis de ambiente de `compose.yaml`. O seu
  `config.py` local não entra na imagem. A senha e a chave de `compose.yaml`
  servem só para a sua máquina.
- **Mudança no código:** a imagem guarda uma cópia do código. Depois de mudar um
  arquivo, inclusive CSS e JavaScript, rode `docker compose up --build` de novo.
  O contêiner `app` roda o `collectstatic` a cada partida. As sessões ficam no
  banco, então ninguém é desconectado.
- **Mudança no esquema:** o `app` só cria a tabela `recados` quando ela não
  existe, para não apagar os dados a cada partida. Depois de mudar o
  `schema.sql`, rode `docker compose down -v`, que apaga os dados, e suba de
  novo.

O `compose.yaml` serve só para desenvolvimento: a senha e a `SECRET_KEY`
estão no próprio arquivo, e a conexão usa HTTP simples, sem HTTPS. A decisão
D22, em [docs/decisoes.md](docs/decisoes.md), explica o que foi escolhido e
por quê.

## Instalar no Debian ou no Ubuntu

### 1. Instalar os pacotes

Escolha uma das duas linhas.

Com nginx e Gunicorn (o Gunicorn vem pelo `pip`, no passo 3):

```bash
sudo apt install nginx python3-venv postgresql
```

Com Apache e mod_wsgi:

```bash
sudo apt install apache2 libapache2-mod-wsgi-py3 python3-venv postgresql
```

### 2. Colocar o projeto em `/var/www/mini-mural`

O servidor web roda com o usuário `www-data`, que em geral não consegue ler
pastas dentro de `/home`. As configurações de `servidor/` apontam para
`/var/www/mini-mural`. Crie a pasta, passe a posse para você e copie o projeto
para lá:

```bash
sudo mkdir -p /var/www/mini-mural
```

```bash
sudo chown "$USER" /var/www/mini-mural
```

```bash
cp -r . /var/www/mini-mural
```

O último comando roda dentro da pasta do projeto. Os passos seguintes rodam em
`/var/www/mini-mural`. Se preferir outra pasta, troque o caminho nos arquivos
de `servidor/`.

### 3. Criar o ambiente virtual e instalar as dependências

O ambiente virtual `.venv` guarda o Django e as outras bibliotecas só para este
projeto. Crie-o com o `python3` do sistema, que é o mesmo para o qual o
mod_wsgi foi compilado:

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

Se você copiou uma pasta `.venv` de outra máquina no passo 2, apague-a antes:
um ambiente virtual só funciona na máquina e na versão de Python em que foi
criado.

### 4. Criar o usuário e o banco no PostgreSQL

A aplicação conecta com um usuário próprio, `mini_mural` (decisão D9). O
primeiro comando pede a senha que você vai escolher:

```bash
sudo -u postgres createuser --pwprompt mini_mural
```

```bash
sudo -u postgres createdb --owner mini_mural mini_mural
```

### 5. Configurar

```bash
cp config.exemplo.py config.py
```

Abra o `config.py` e troque `senha` pela senha escolhida no passo 4. Troque
também a `SECRET_KEY` por uma chave nova, gerada com:

```bash
.venv/bin/python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Os outros valores já correspondem ao que você criou. O `config.py` fica fora
do Git. Confira a configuração com:

```bash
.venv/bin/python manage.py check
```

### 6. Criar as tabelas

As tabelas vêm de dois lugares, nesta ordem. Primeiro, as migrations do Django
criam as tabelas de usuários (`auth_user`) e de sessões:

```bash
.venv/bin/python manage.py migrate
```

Depois, o comando `carregar_esquema` roda o `sql/schema.sql`, que cria a tabela
`recados`. Ela aponta para `auth_user`, por isso vem depois. A opção
`--exemplos` cria também o usuário `exemplo`, com a senha `senha-de-exemplo`, e
os recados de exemplo; use esse usuário só na sua máquina:

```bash
.venv/bin/python manage.py carregar_esquema --exemplos
```

O `schema.sql` começa com `DROP TABLE recados`: rodar o comando de novo apaga
todos os recados (os usuários ficam). É assim que o mural muda de esquema, já
que não usa migrations.

### 7. Copiar os arquivos estáticos

O `collectstatic` copia o CSS e o JavaScript para a pasta `staticfiles/`, que o
servidor web entrega direto:

```bash
.venv/bin/python manage.py collectstatic
```

### 8. Ligar o site no servidor web

Com nginx e Gunicorn, ligue primeiro o Gunicorn como serviço:

```bash
sudo cp servidor/mini-mural.service /etc/systemd/system/
```

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl enable --now mini-mural
```

Depois, o site no nginx:

```bash
sudo cp servidor/nginx.conf /etc/nginx/sites-available/mini-mural
```

```bash
sudo ln -s /etc/nginx/sites-available/mini-mural /etc/nginx/sites-enabled/
```

```bash
sudo nginx -t
```

```bash
sudo systemctl reload nginx
```

Com Apache:

```bash
sudo cp servidor/apache.conf /etc/apache2/sites-available/mini-mural.conf
```

```bash
sudo a2ensite mini-mural
```

```bash
sudo systemctl reload apache2
```

### 9. Abrir

Abra <http://localhost:8081>. As configurações usam a porta 8081 porque a 80
já é do site padrão do servidor, e a 8080, do site padrão do nginx no Homebrew.

## Depois de mudar o código

O Gunicorn e o mod_wsgi carregam o código Python uma vez e o mantêm na memória.
Depois de mudar um arquivo `.py` ou um template, reinicie o Gunicorn:

```bash
sudo systemctl restart mini-mural
```

Ou recarregue o Apache:

```bash
sudo systemctl reload apache2
```

Depois de mudar um CSS ou um JavaScript, rode o `collectstatic` de novo (passo
7). Sem isso, o navegador continua recebendo a versão anterior.

## No macOS

Use nginx com Gunicorn, instalados pelo Homebrew e pelo `pip`. O Apache que vem
com o macOS não traz o mod_wsgi.

```bash
brew install postgresql@18 nginx python
```

As diferenças em relação aos passos do Debian são estas:

- **Passo 2:** o projeto pode ficar onde está. Troque `/var/www/mini-mural` em
  `servidor/nginx.conf` pela pasta do projeto.
- **Passo 3:** crie o ambiente virtual com o `python3` do Homebrew.
- **Passo 4:** o PostgreSQL do Homebrew usa o seu usuário do macOS como
  administrador. Rode `createuser` e `createdb` sem o `sudo -u postgres`. Antes,
  ponha os comandos no `PATH` e ligue o banco:

  ```bash
  echo 'export PATH="$(brew --prefix postgresql@18)/bin:$PATH"' >> ~/.zshrc
  ```

  ```bash
  brew services start postgresql@18
  ```

- **Passo 8:** no lugar do systemd, ligue o Gunicorn em um terminal, na pasta
  do projeto, e deixe o terminal aberto:

  ```bash
  .venv/bin/gunicorn mini_mural.wsgi --bind 127.0.0.1:8000
  ```

  Em outro terminal, copie o site para a pasta de sites do nginx e ligue-o:

  ```bash
  cp servidor/nginx.conf "$(brew --prefix)/etc/nginx/servers/mini-mural.conf"
  ```

  ```bash
  brew services start nginx
  ```

  Para aplicar mudanças no código Python, interrompa o Gunicorn com Ctrl+C e
  ligue-o de novo.

## Conferir

Rode os testes das regras, que não precisam de banco nem de servidor:

```bash
.venv/bin/python manage.py test
```

Com o site no ar, exercite o mural no navegador:

1. Abra <http://localhost:8081>. Sem login, o navegador vai para a tela de
   entrar.
2. Crie uma conta em "Criar conta". Um nome que já existe, mesmo com outras
   maiúsculas, ou uma senha fraca, como `12345678`, mostram a mensagem no campo.
3. Clique em Publicar com o campo vazio. A mensagem aparece e o foco volta ao
   campo.
4. Publique um recado privado e outro com a caixa "Público" marcada. Os dois
   aparecem no topo da lista com o seu nome.
5. Arquive um recado pela lista e outro pelo detalhe. Os dois passam a mostrar
   "Arquivado".
6. Em Sobre, escolha "Mais antigos primeiro", salve e volte ao Mural. A ordem se
   inverte e continua assim depois de recarregar.
7. Clique em Sair e abra o endereço do recado público. Ele aparece sem o botão
   de arquivar. O endereço do recado privado leva à tela de entrar.

O login diferencia maiúsculas de minúsculas no nome de usuário: a conta
`exemplo` não entra como `Exemplo`. O cadastro, por outro lado, recusa um nome
que só difere de outro nas maiúsculas.

Confira também pelo terminal. Sem login, o mural responde `302`, um
redirecionamento para a tela de entrar:

```bash
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://localhost:8081/
```

Com os exemplos carregados, o recado 3 é público e responde `200` sem login:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8081/recado/3/
```

Um POST sem o token CSRF recebe `403`, mesmo com usuário e senha certos:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -d 'username=exemplo&password=senha-de-exemplo' http://localhost:8081/entrar/
```

E o servidor não entrega o código nem a configuração. A resposta deve ser
`404`:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8081/config.py
```

## Estrutura

```text
mini-mural/
├── manage.py                # Linha de comando do Django
├── requirements.txt         # Django, psycopg e Gunicorn
├── config.exemplo.py        # Modelo da configuração; copie para config.py
├── compose.yaml             # Serviços do Docker: web, app e banco
├── docker/
│   ├── Dockerfile           # Imagem com Python, Django e Gunicorn
│   ├── nginx.conf           # Site do nginx dentro do contêiner
│   └── config.py            # Configuração lida das variáveis de ambiente
├── mini_mural/              # Projeto: configuração e entrada WSGI
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── mural/                   # App: tudo o que é do mural
│   ├── models.py            # Recado, sobre a tabela do schema.sql
│   ├── recados.py           # Todas as consultas de recados
│   ├── validacao.py         # Regra do texto do recado
│   ├── preferencias.py      # Cookie da ordem
│   ├── views.py             # Views do mural, do login e do cadastro
│   ├── urls.py              # Endereços
│   ├── tests.py             # Testes das regras sem banco
│   ├── management/commands/
│   │   └── carregar_esquema.py  # Roda o schema.sql e o seed.sql
│   ├── templates/           # Páginas, login, cadastro, 404 e 500
│   └── static/mural/        # CSS e JavaScript
├── servidor/
│   ├── nginx.conf           # Site para nginx na frente do Gunicorn
│   ├── mini-mural.service   # Gunicorn como serviço do systemd
│   └── apache.conf          # Site para Apache com mod_wsgi
├── sql/
│   ├── schema.sql           # Cria a tabela recados (apaga a anterior)
│   └── seed.sql             # Recados de exemplo
└── docs/                    # Decisões, funcionamento e diagramas
```

## Problemas comuns

O detalhe de quase todo erro está no log. Com Gunicorn, leia
`sudo journalctl -u mini-mural`; com Apache, leia
`/var/log/apache2/mini-mural-erro.log`; com Docker, leia
`docker compose logs app`.

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Página "Algo deu errado" e `password authentication failed` no log | Senha do `config.py` diferente da escolhida | Corrija `senha` no `config.py` e reinicie |
| Página "Algo deu errado" e `Connection refused` no log | O PostgreSQL está desligado | `sudo systemctl start postgresql` |
| `relation "recados" does not exist` no log | O esquema do mural não foi carregado | Rode o `carregar_esquema` do passo 6 |
| `relation "auth_user" does not exist` ao rodar o `carregar_esquema` | O `migrate` não rodou antes | Rode o `migrate` e depois o `carregar_esquema` |
| `relation "django_session" does not exist` no log | O `migrate` não rodou | Rode o `migrate` do passo 6 |
| `column recados.autor_id does not exist` no log | A tabela `recados` é de uma etapa anterior | Rode `carregar_esquema --exemplos`, sem `--se-ausente`, que recria a tabela e apaga os recados |
| `column recados.autor_id does not exist` no log (Docker) | O volume `dados` veio de uma etapa anterior, e o `app` não recria a tabela que já existe | `docker compose down -v` e suba outra vez; os dados se perdem |
| Login recusado com usuário e senha que parecem certos | O nome foi digitado com outras maiúsculas | Digite o nome exatamente como no cadastro |
| `Bad Request (400)` | O nome do site não está em `ENDERECOS_ACEITOS` | Acrescente o nome no `config.py` e reinicie |
| `502 Bad Gateway` (nginx) | O Gunicorn não está rodando | Leia `sudo journalctl -u mini-mural`; a causa mais comum é falta do `config.py` |
| Página sem estilo | O `collectstatic` não rodou, ou o `alias` aponta para outra pasta | Rode o passo 7 e confira o caminho de `/static/` |
| `403 Forbidden` ao enviar um formulário | O POST chegou sem o token CSRF, ou o token mudou depois do login | Recarregue a página antes de enviar; o formulário precisa do `{% csrf_token %}` |
| Mudança no código não aparece | O Gunicorn ou o Apache ainda usam o código antigo | Veja "Depois de mudar o código" |
| `Cannot connect to the Docker daemon` (Docker) | O Docker não está ligado | Abra o Docker Desktop, ou ligue o serviço do Docker |
| `port is already allocated` (Docker) | Outro programa já usa a porta 8081, como o nginx da instalação direta | Desligue o outro programa, ou troque `"8081:80"` em `compose.yaml` por outra porta |
| Mudança no esquema não aparece (Docker) | A tabela `recados` já existia, e o `app` não a recria | `docker compose down -v` e suba outra vez |
