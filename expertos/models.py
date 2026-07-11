from django.db import models


class Experto(models.Model):
    nom_expert = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nombre')
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'experts'
        verbose_name = 'Experto'
        verbose_name_plural = 'Expertos'

    def __str__(self):
        return self.nom_expert or ''
