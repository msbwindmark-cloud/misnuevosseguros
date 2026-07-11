from django.db import models


class TypeAttestation(models.Model):
    type_attestation = models.CharField(max_length=100)
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'type_attestation'
        verbose_name = 'Tipo de atestación'
        verbose_name_plural = 'Tipos de atestación'

    def __str__(self):
        return self.type_attestation


class Attestation(models.Model):
    id_type_attestation = models.ForeignKey(TypeAttestation, on_delete=models.CASCADE, db_column='id_type_attestation')
    numero_attestation = models.CharField(max_length=100)
    seleccionado = models.BooleanField(default=True)
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attestation'
        verbose_name = 'Atestación'
        verbose_name_plural = 'Atestaciones'
        ordering = ['-id']

    def __str__(self):
        return f"{self.id_type_attestation.type_attestation} - {self.numero_attestation}"
