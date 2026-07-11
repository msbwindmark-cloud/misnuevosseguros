from django.db import models


class CiudadSalat(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad_api = models.CharField(max_length=100)
    pais_api = models.CharField(max_length=100)
    metodo = models.IntegerField(default=2, help_text='1=Karachi 2=ISNA 3=MWL 4=UmmAlQura 5=Egypt 8=Gulf')
    grupo = models.CharField(max_length=50, default='Otros')
    activa = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Ciudad Salat'
        verbose_name_plural = 'Ciudades Salat'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return f'{self.nombre} ({self.pais_api})'
