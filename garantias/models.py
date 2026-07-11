from django.db import models


class Garantia(models.Model):
    nom_garantie = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nombre')
    has_configuration = models.BooleanField(default=False, verbose_name='Tiene configuración')

    class Meta:
        db_table = 'garanties'
        verbose_name = 'Garantía'
        verbose_name_plural = 'Garantías'

    def __str__(self):
        return self.nom_garantie or ''


class GarantiaOption(models.Model):
    garantia = models.ForeignKey(Garantia, on_delete=models.CASCADE, related_name='opciones')
    nom_option = models.CharField(max_length=100, blank=True, null=True, verbose_name='Opción')
    requires_montant = models.BooleanField(default=False, verbose_name='Requiere monto')

    class Meta:
        db_table = 'garantie_options'
        verbose_name = 'Opción de garantía'
        verbose_name_plural = 'Opciones de garantía'

    def __str__(self):
        return self.nom_option or ''


class GarantiaFranchise(models.Model):
    option = models.ForeignKey(GarantiaOption, on_delete=models.CASCADE, related_name='franquicias')
    nom_franchise = models.CharField(max_length=100, blank=True, null=True, verbose_name='Franquicia')

    class Meta:
        db_table = 'garantie_franchises'
        verbose_name = 'Franquicia'
        verbose_name_plural = 'Franquicias'

    def __str__(self):
        return self.nom_franchise or ''
