from django.db import models


class Banco(models.Model):
    nom_banque = models.CharField(max_length=200, verbose_name='Nombre del banco')
    compte_banque = models.CharField(max_length=200, verbose_name='Cuenta')
    address_banque = models.TextField(blank=True, default='', verbose_name='Dirección')
    distrit_banque = models.CharField(max_length=200, blank=True, default='', verbose_name='Distrito')
    ville_banque = models.CharField(max_length=200, blank=True, default='', verbose_name='Ciudad')
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'banque'
        verbose_name = 'Banco'
        verbose_name_plural = 'Bancos'

    def __str__(self):
        return self.nom_banque


class Benificiario(models.Model):
    nom_benificiaire = models.CharField(max_length=200, verbose_name='Nombre')
    banque_benificiaire = models.CharField(max_length=200, verbose_name='Banco')
    compte_benificiaire = models.CharField(max_length=200, verbose_name='Cuenta')
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'benificiare'
        verbose_name = 'Beneficiario'
        verbose_name_plural = 'Beneficiarios'

    def __str__(self):
        return self.nom_benificiaire


class EnvioBanco(models.Model):
    nom_envoie = models.CharField(max_length=200, verbose_name='Nombre')
    banque_envoie = models.CharField(max_length=200, verbose_name='Banco')
    compte_envoie = models.CharField(max_length=200, verbose_name='Cuenta')
    date_envoie = models.DateField(blank=True, null=True, verbose_name='Fecha de envío')
    montant_envoie = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    motif_envoie = models.TextField(verbose_name='Motivo')
    benificiario = models.ForeignKey(Benificiario, on_delete=models.CASCADE, related_name='envios')
    banco = models.ForeignKey(Banco, on_delete=models.CASCADE, related_name='envios')
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'les_envoies'
        verbose_name = 'Envío bancario'
        verbose_name_plural = 'Envíos bancarios'
        ordering = ['-id']

    def __str__(self):
        return f"Envío {self.id} - {self.nom_envoie}"
