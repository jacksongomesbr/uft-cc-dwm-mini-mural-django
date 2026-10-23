# Documentação do Mini Mural em Django

Esta pasta explica o projeto para quem vai ler, rodar ou modificar o código.
Para instalar e rodar, comece pelo [README da raiz](../README.md).

| Documento | Responde a |
|---|---|
| [funcionamento.md](funcionamento.md) | O que a aplicação faz e qual o caminho de cada pedido entre navegador, servidor web, Django e PostgreSQL |
| [decisoes.md](decisoes.md) | Por que o projeto é assim: cada decisão com a alternativa descartada e a consequência aceita |
| [modelo-de-dados.md](modelo-de-dados.md) | Tabelas, modelo `Recado`, sessão, ciclo de vida de um recado e o SQL de cada consulta |
| [estrutura.md](estrutura.md) | Onde fica cada coisa e o que pode depender do quê |

O projeto evolui por etapas, cada uma em um ramo; a tabela está no README da
raiz. Esta documentação descreve a etapa do ramo em que você está.

Os diagramas usam Mermaid. O GitHub e o VS Code, com a extensão de pré-visualização
de Markdown, desenham os diagramas direto no arquivo.

## O projeto em um parágrafo

O Mini Mural é uma aplicação web em que o servidor monta cada página. O
navegador pede um endereço, o nginx ou o Apache entrega o pedido ao Django, a
view consulta o PostgreSQL pelo ORM e devolve HTML montado por um template.
Publicar, arquivar e escolher a ordem são formulários comuns enviados por POST,
seguidos de um redirecionamento. O login usa o `django.contrib.auth`. Quem não entrou
vê só os recados públicos ainda publicados; o resto exige login, e só o autor
arquiva o próprio recado. O JavaScript só melhora o formulário de
recado; sem ele, tudo continua funcionando. O projeto usa do Django só o
essencial (URLs, views, templates, ORM, estáticos, CSRF e autenticação) para que cada parte
do caminho fique visível. Para rodar na própria máquina sem instalar Python e
PostgreSQL, há um `compose.yaml` com Docker (decisão D22).
