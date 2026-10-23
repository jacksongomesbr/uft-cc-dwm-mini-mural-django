-- Esquema do Mini Mural.
--
-- Execute com o banco já criado, conectado como o usuário da aplicação, para
-- que a tabela pertença a ele:
--   psql -h localhost -U mini_mural -d mini_mural -f sql/schema.sql
--
-- ATENÇÃO: o arquivo começa apagando a tabela. Rodar de novo zera os recados.
-- Este projeto não usa migrations: quando o esquema muda, você edita este
-- arquivo e roda outra vez.

DROP TABLE IF EXISTS recados;

CREATE TABLE recados (
    id        bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    texto     text        NOT NULL,
    criado_em timestamptz NOT NULL DEFAULT now(),
    status    text        NOT NULL DEFAULT 'publicado',

    -- As mesmas regras que o Python confere. Se um defeito no código deixar passar
    -- um recado inválido, o banco recusa a gravação.
    CONSTRAINT recado_texto_preenchido CHECK (btrim(texto) <> ''),
    CONSTRAINT recado_texto_ate_280    CHECK (char_length(texto) <= 280),
    CONSTRAINT recado_status_valido    CHECK (status IN ('publicado', 'arquivado'))
);

-- A lista do mural sempre ordena por data de criação.
CREATE INDEX recados_criado_em ON recados (criado_em);
