from django.conf import settings
from django.db import models
from django.db.models.functions import Now


class Recado(models.Model):
    """Uma linha da tabela recados.

    A tabela é criada por sql/schema.sql, e não por migrations. O
    managed = False diz ao Django para usar a tabela como está, sem criar,
    alterar nem apagar nada. Quando o schema.sql muda, este modelo muda junto.

    O autor aponta para o usuário do django.contrib.auth (tabela auth_user),
    esse sim criado pelas migrations do Django.
    """

    PUBLICADO = 'publicado'
    ARQUIVADO = 'arquivado'

    # bigint gerado pelo banco (GENERATED ALWAYS AS IDENTITY).
    id = models.BigAutoField(primary_key=True)
    texto = models.TextField()
    # db_default: o valor vem do DEFAULT da tabela, e não do Python.
    criado_em = models.DateTimeField(db_default=Now())
    status = models.TextField(db_default=PUBLICADO)
    # Coluna autor_id. PROTECT impede apagar um usuário que tem recados, como
    # o REFERENCES da tabela.
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='recados'
    )
    # Recado público pode ser lido sem login. Todo recado nasce privado.
    publico = models.BooleanField(db_default=False)
    # Instante do arquivamento; None enquanto o recado está publicado.
    arquivado_em = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = 'recados'

    @property
    def arquivado(self):
        return self.status == self.ARQUIVADO

    @property
    def leitura_publica(self):
        """Um recado público e ainda publicado pode ser lido sem login."""
        return self.publico and not self.arquivado

    def pode_ser_visto_por(self, usuario):
        """Recado arquivado, só o autor vê; publicado e privado, qualquer
        usuário logado; publicado e público, qualquer pessoa."""
        if self.arquivado:
            return usuario.is_authenticated and self.autor_id == usuario.id
        return usuario.is_authenticated or self.publico

    def pode_ser_arquivado_por(self, usuario):
        """Só o autor arquiva, e só enquanto o recado está publicado."""
        return (
            usuario.is_authenticated
            and not self.arquivado
            and self.autor_id == usuario.id
        )

    def __str__(self):
        return self.texto
