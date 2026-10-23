-- Recados de exemplo, todos do usuário exemplo.
--
-- O comando "python manage.py carregar_esquema --exemplos" cria o usuário
-- exemplo (senha: senha-de-exemplo) e depois roda este arquivo. Use esse
-- usuário só na sua máquina.
--
-- As datas são diferentes de propósito: com todas iguais, trocar a ordem do
-- mural em "Sobre" não mudaria nada na tela. O terceiro recado é público e
-- pode ser lido sem login em /recado/3/.

INSERT INTO recados (texto, criado_em, status, publico, autor_id)
SELECT exemplos.texto, exemplos.criado_em::timestamptz, exemplos.status,
       exemplos.publico, auth_user.id
  FROM (VALUES
        ('Entrega do relatório adiada.',           '2026-03-10 16:45:00-03', 'arquivado', false),
        ('A chave da sala 3 está na coordenação.', '2026-03-11 09:20:00-03', 'publicado', false),
        ('Reunião de equipe na quinta, às 14h.',   '2026-03-12 14:02:00-03', 'publicado', true)
       ) AS exemplos (texto, criado_em, status, publico)
 CROSS JOIN auth_user
 WHERE auth_user.username = 'exemplo';
