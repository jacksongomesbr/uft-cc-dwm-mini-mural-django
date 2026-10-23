from django.db import models
from django.db.models.functions import Now


class Recado(models.Model):
    """Uma linha da tabela recados.

    A tabela é criada por sql/schema.sql, e não por migrations. O
    managed = False diz ao Django para usar a tabela como está, sem criar,
    alterar nem apagar nada. Quando o schema.sql muda, este modelo muda junto.
    """

    PUBLICADO = 'publicado'
    ARQUIVADO = 'arquivado'

    # bigint gerado pelo banco (GENERATED ALWAYS AS IDENTITY).
    id = models.BigAutoField(primary_key=True)
    texto = models.TextField()
    # db_default: o valor vem do DEFAULT da tabela, e não do Python.
    criado_em = models.DateTimeField(db_default=Now())
    status = models.TextField(db_default=PUBLICADO)

    class Meta:
        managed = False
        db_table = 'recados'

    @property
    def arquivado(self):
        return self.status == self.ARQUIVADO

    def __str__(self):
        return self.texto
