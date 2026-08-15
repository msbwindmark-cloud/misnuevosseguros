from django.db import models


class Cliente(models.Model):
    code_client = models.IntegerField(unique=True, verbose_name='Código')
    nom_client = models.TextField(verbose_name='Nombre')
    telephone_client = models.CharField(max_length=100, blank=True, default='', verbose_name='Teléfono')
    email_client = models.CharField(max_length=100, blank=True, default='', verbose_name='Email')
    address_client = models.TextField(blank=True, default='', verbose_name='Adresse')
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')

    class Meta:
        db_table = 'liste_des_clients'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['code_client']

    def __str__(self):
        return f"{self.code_client} - {self.nom_client}"


class ClienteEliminado(models.Model):
    code_client = models.IntegerField(verbose_name='Código')
    nom_client = models.TextField(verbose_name='Nombre')
    telephone_client = models.CharField(max_length=100, blank=True, default='', verbose_name='Teléfono')
    email_client = models.CharField(max_length=100, blank=True, default='', verbose_name='Email')
    address_client = models.TextField(blank=True, default='', verbose_name='Adresse')
    eliminado_el = models.DateTimeField(auto_now_add=True, verbose_name='Eliminado el')

    class Meta:
        db_table = 'clientes_eliminados'
        verbose_name = 'Cliente eliminado'
        verbose_name_plural = 'Clientes eliminados'

    def __str__(self):
        return f"{self.code_client} - {self.nom_client}"
