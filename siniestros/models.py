from django.db import models
from polizas.models import Poliza


class Formule(models.Model):
    nom_formule = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'formule'
        verbose_name = 'Fórmula'
        verbose_name_plural = 'Fórmulas'

    def __str__(self):
        return self.nom_formule or ''


class ReferenceReglement(models.Model):
    nom_reference_reglement = models.CharField(max_length=100)

    class Meta:
        db_table = 'reference_reglement'
        verbose_name = 'Referencia de reglamento'
        verbose_name_plural = 'Referencias de reglamento'

    def __str__(self):
        return self.nom_reference_reglement


class DocumentDeBase(models.Model):
    nom_document_de_base = models.CharField(max_length=100)

    class Meta:
        db_table = 'document_de_base'
        verbose_name = 'Documento de base'
        verbose_name_plural = 'Documentos de base'

    def __str__(self):
        return self.nom_document_de_base


class Sinistro(models.Model):
    code_sinistre = models.CharField(max_length=100, blank=True, null=True, verbose_name='Código siniestro')
    ref_sinistre = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ref. siniestro')
    date_operation = models.DateField(verbose_name='Fecha de operación', null=True, blank=True)
    date_sinistre = models.DateField(verbose_name='Fecha del siniestro', null=True, blank=True)
    date_reception = models.DateField(verbose_name='Fecha de recepción', null=True, blank=True)
    police = models.CharField(max_length=100, verbose_name='Póliza')
    nom_formule = models.CharField(max_length=100, blank=True, null=True, verbose_name='Fórmula')
    assure = models.CharField(max_length=100, verbose_name='Asegurado')
    categorie_assurance = models.CharField(max_length=100, verbose_name='Categoría')
    reference_assurance = models.CharField(max_length=100, verbose_name='Referencia')
    benificiaire = models.CharField(max_length=100, verbose_name='Beneficiario')
    reference_assistance = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ref. asistencia')
    nom_expert = models.CharField(max_length=100, blank=True, null=True, verbose_name='Experto')
    reference_reglement = models.CharField(max_length=100, verbose_name='Ref. reglamento')
    document_de_base = models.CharField(max_length=100, blank=True, null=True, verbose_name='Documento base')
    reference_payement = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ref. pago')
    montant = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Monto')
    date_payement = models.DateField(blank=True, null=True, verbose_name='Fecha de pago')
    cod_sig_correcto = models.BooleanField(default=False, verbose_name='Código correcto')
    poliza = models.ForeignKey(Poliza, on_delete=models.SET_NULL, null=True, blank=True, related_name='siniestros')
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'table_sinistres'
        verbose_name = 'Siniestro'
        verbose_name_plural = 'Siniestros'
        ordering = ['-id']

    def __str__(self):
        return f"Siniestro {self.id} - {self.assure}"


class DocumentoSinistro(models.Model):
    code_sinistre = models.CharField(max_length=50, blank=True, default='')
    nombre_archivo = models.CharField(max_length=255, blank=True, default='')
    tipo_documento = models.IntegerField(blank=True, null=True)
    ruta_archivo = models.CharField(max_length=255, blank=True, default='')
    archivo = models.FileField(upload_to='uploads_sinistres/', blank=True)
    id_documento_usuario_origen = models.IntegerField(blank=True, null=True)
    sinistro = models.ForeignKey(Sinistro, on_delete=models.CASCADE, related_name='documentos', null=True, blank=True)

    class Meta:
        db_table = 'documentos_sinistres'
        verbose_name = 'Documento de siniestro'
        verbose_name_plural = 'Documentos de siniestros'

    def __str__(self):
        return self.nombre_archivo or ''
