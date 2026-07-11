from django.db import models
from clientes.models import Cliente


class TipoAffaire(models.TextChoices):
    AFFAIRE_NOUVELLE = 'Affaire nouvelle', 'Affaire nouvelle'
    RENOUVELLEMENT = 'Renouvellement', 'Renouvellement'
    CHANGEMENT_VEHICULE = 'Changement vehicule', 'Changement vehicule'
    DUPLICATA = 'Duplicata', 'Duplicata'
    RESILIATION = 'Resiliation', 'Resiliation'
    AUTRE_PROVISOIRE = 'Autre provisoire', 'Autre provisoire'
    ATTESTATION_DEFINITIVE = "Attestation définitive", "Attestation définitive"
    AUTRES = 'Autres', 'Autres'
    CARTE_VERTE = 'Carte Verte', 'Carte Verte'
    REGULARISATION_PRIME = 'Régularisation de prime', 'Régularisation de prime'
    COMPLEMENT_PAIEMENT = 'Complement de paiment', 'Complement de paiment'
    PRECISION = 'PRECISION', 'PRECISION'


class Poliza(models.Model):
    recu = models.AutoField(primary_key=True, verbose_name='Recibo nº')
    fecha_hoy = models.DateField(blank=True, null=True, verbose_name='Fecha')
    letype = models.CharField(max_length=50, choices=TipoAffaire.choices, verbose_name='Tipo')
    attestation = models.CharField(max_length=100, blank=True, default='', verbose_name='Atestación')
    police = models.CharField(max_length=100, blank=True, default='', verbose_name='Póliza')
    marque = models.CharField(max_length=200, blank=True, default='', verbose_name='Marca')
    matricule = models.CharField(max_length=50, blank=True, default='', verbose_name='Matrícula')
    produit = models.CharField(max_length=200, blank=True, default='', verbose_name='Producto')
    designation = models.CharField(max_length=200, blank=True, default='', verbose_name='Designación')
    assure = models.CharField(max_length=100, blank=True, default='', verbose_name='Asegurado')
    prenom = models.CharField(max_length=100, blank=True, default='', verbose_name='Apellido')
    du = models.DateField(blank=True, null=True, verbose_name='Desde')
    au = models.DateField(blank=True, null=True, verbose_name='Hasta')
    prime_net = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Prima neta')
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Impuestos')
    tp = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='TP')
    accesoires = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Accesorios')
    totale = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total')
    espece = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Efectivo')
    cheque = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Cheque')
    virement = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Transferencia')
    reste = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Resto')
    date_versement = models.DateField(blank=True, null=True, verbose_name='Fecha de pago')
    mode_paiment = models.CharField(max_length=20, default='nulo', verbose_name='Modo de pago')
    code_client = models.CharField(max_length=20, blank=True, default='', verbose_name='Código cliente')
    telefono = models.CharField(max_length=50, blank=True, default='', verbose_name='Teléfono')
    email = models.CharField(max_length=100, blank=True, default='', verbose_name='Email')
    address_client = models.TextField(blank=True, default='', verbose_name='Dirección')
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')

    class Meta:
        db_table = 'proyectosis'
        verbose_name = 'Póliza'
        verbose_name_plural = 'Pólizas'
        ordering = ['-recu']

    def __str__(self):
        return f"Recibo {self.recu} - {self.assure}"


class PolizaEliminada(models.Model):
    recu = models.IntegerField(primary_key=True)
    fecha_hoy = models.DateField(blank=True, null=True)
    letype = models.CharField(max_length=50, blank=True, default='')
    attestation = models.CharField(max_length=100, blank=True, default='')
    police = models.CharField(max_length=100, blank=True, default='')
    matricule = models.CharField(max_length=50, blank=True, default='')
    produit = models.CharField(max_length=200, blank=True, default='')
    assure = models.CharField(max_length=100, blank=True, default='')
    du = models.DateField(blank=True, null=True)
    au = models.DateField(blank=True, null=True)
    totale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    espece = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cheque = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    virement = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reste = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_versement = models.DateField(blank=True, null=True)
    mode_paiment = models.CharField(max_length=20, default='nulo')
    cree_le = models.DateTimeField()

    class Meta:
        db_table = 'proyectosis_elimines'
        verbose_name = 'Póliza eliminada'
        verbose_name_plural = 'Pólizas eliminadas'


class PolizaGarantia(models.Model):
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE, related_name='garantias')
    garantia = models.ForeignKey('garantias.Garantia', on_delete=models.CASCADE)
    valeur = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Valor')

    class Meta:
        db_table = 'proyectosis_garantie'
        unique_together = ('poliza', 'garantia')
        verbose_name = 'Garantía de póliza'
        verbose_name_plural = 'Garantías de pólizas'


class PolizaGarantiaOption(models.Model):
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE, related_name='garantias_options')
    garantia = models.ForeignKey('garantias.Garantia', on_delete=models.CASCADE)
    option = models.ForeignKey('garantias.GarantiaOption', on_delete=models.CASCADE)
    valeur = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'proyectosis_garantie_options'
        unique_together = ('poliza', 'garantia', 'option')
        verbose_name = 'Opción de garantía de póliza'
        verbose_name_plural = 'Opciones de garantía de pólizas'


class PolizaCopia(models.Model):
    poliza_original = models.OneToOneField(Poliza, on_delete=models.CASCADE, primary_key=True, related_name='copia')
    copiado_el = models.DateTimeField(auto_now_add=True)
    fecha_hoy = models.DateField(blank=True, null=True)
    letype = models.CharField(max_length=50, blank=True, default='')
    attestation = models.CharField(max_length=100, blank=True, default='')
    police = models.CharField(max_length=100, blank=True, default='')
    marque = models.CharField(max_length=200, blank=True, default='')
    matricule = models.CharField(max_length=50, blank=True, default='')
    produit = models.CharField(max_length=200, blank=True, default='')
    designation = models.CharField(max_length=200, blank=True, default='')
    assure = models.CharField(max_length=100, blank=True, default='')
    du = models.DateField(blank=True, null=True)
    au = models.DateField(blank=True, null=True)
    prime_net = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    accesoires = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    totale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    espece = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cheque = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    virement = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reste = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'proyectosis_copia'
        verbose_name = 'Copia de póliza'
        verbose_name_plural = 'Copias de pólizas'

    def __str__(self):
        return f"Copia recibo {self.poliza_original_id}"


class PolizaGarantiaFranchise(models.Model):
    poliza = models.ForeignKey(Poliza, on_delete=models.CASCADE, related_name='garantias_franquicias')
    garantia = models.ForeignKey('garantias.Garantia', on_delete=models.CASCADE)
    option = models.ForeignKey('garantias.GarantiaOption', on_delete=models.CASCADE)
    franchise = models.ForeignKey('garantias.GarantiaFranchise', on_delete=models.CASCADE)
    montant_franchise = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'proyectosis_garantie_franchises'
        unique_together = ('poliza', 'garantia', 'option')
        verbose_name = 'Franquicia de garantía de póliza'
        verbose_name_plural = 'Franquicias de garantía de pólizas'
