-- Recados de exemplo.
--
-- Opcional. Execute depois do schema.sql:
--   psql -h localhost -U mini_mural -d mini_mural -f sql/seed.sql
--
-- As datas são diferentes de propósito: com todas iguais, trocar a ordem do
-- mural em "Sobre" não mudaria nada na tela.

INSERT INTO recados (texto, criado_em, status) VALUES
    ('Entrega do relatório adiada.',           '2026-03-10 16:45:00-03', 'arquivado'),
    ('A chave da sala 3 está na coordenação.', '2026-03-11 09:20:00-03', 'publicado'),
    ('Reunião de equipe na quinta, às 14h.',   '2026-03-12 14:02:00-03', 'publicado');
