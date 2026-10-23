-- Esquema do mural.
--
-- A tabela recados depende de auth_user, criada pelas migrations do Django.
-- Por isso este arquivo roda DEPOIS do migrate, pelo comando:
--   python manage.py carregar_esquema
--
-- ATENÇÃO: o arquivo começa apagando a tabela recados. Rodar de novo zera os
-- recados (os usuários, em auth_user, ficam). Este projeto não usa migrations
-- para o mural: quando o esquema muda, você edita este arquivo e roda outra vez.

DROP TABLE IF EXISTS recados;

CREATE TABLE recados (
    id        bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    texto     text        NOT NULL,
    criado_em timestamptz NOT NULL DEFAULT now(),
    status    text        NOT NULL DEFAULT 'publicado',
    -- Quem publicou. O tipo acompanha o de auth_user.id, que é integer. Um
    -- usuário com recados não pode ser apagado.
    autor_id  integer     NOT NULL REFERENCES auth_user (id),
    -- Recado público pode ser lido sem login. Todo recado nasce privado.
    publico   boolean     NOT NULL DEFAULT false,

    -- As mesmas regras que o Python confere. Se um defeito no código deixar passar
    -- um recado inválido, o banco recusa a gravação.
    CONSTRAINT recado_texto_preenchido CHECK (btrim(texto) <> ''),
    CONSTRAINT recado_texto_ate_280    CHECK (char_length(texto) <= 280),
    CONSTRAINT recado_status_valido    CHECK (status IN ('publicado', 'arquivado'))
);

-- A lista do mural sempre ordena por data de criação.
CREATE INDEX recados_criado_em ON recados (criado_em);
