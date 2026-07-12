from django.db import models


class Destinataire(models.Model):
    nom_destinataire = models.CharField(max_length=255, verbose_name='Destinatario')
    adresse_destinataire = models.TextField(blank=True, default='', verbose_name='Dirección')
    creado_el = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'destinataire'
        verbose_name = 'Destinatario'
        verbose_name_plural = 'Destinatarios'
    def __str__(self):
        return self.nom_destinataire


class Expediteur(models.Model):
    nom_expediteur = models.CharField(max_length=255, verbose_name='Remitente')
    adresse_expediteur = models.TextField(blank=True, default='', verbose_name='Dirección')
    creado_el = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'expediteur'
        verbose_name = 'Remitente'
        verbose_name_plural = 'Remitentes'
    def __str__(self):
        return self.nom_expediteur


class EnvioCourrier(models.Model):
    date_envoie_courrier = models.DateField(verbose_name='Fecha de envío')
    expediteur_envoie_courrier = models.CharField(max_length=255, verbose_name='Remitente')
    addresse_expediteur_envoie_courrier = models.TextField(blank=True, null=True, verbose_name='Dirección remitente')
    destinataire_envoie_courrier = models.CharField(max_length=255, verbose_name='Destinatario')
    addresse_envoie_courrier = models.TextField(verbose_name='Dirección')
    tipo_documento_envoie_courrier = models.CharField(max_length=10, blank=True, null=True)
    nombre_documento_envoie_courrier = models.CharField(max_length=255, blank=True, null=True)
    tamanio_documento_envoie_courrier = models.BigIntegerField(blank=True, null=True)
    archivo = models.FileField(upload_to='courrier/', blank=True)
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'envoie_courrier'
        verbose_name = 'Envío de correo'
        verbose_name_plural = 'Envíos de correo'
        ordering = ['-id']

    def __str__(self):
        return f"Correo {self.id} - {self.destinataire_envoie_courrier}"
