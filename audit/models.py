from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Modificación'),
        ('DELETE', 'Eliminación'),
    ]
    model_name = models.CharField(max_length=100, verbose_name='Modelo')
    record_id = models.CharField(max_length=50, verbose_name='ID del registro')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name='Acción')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Usuario'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Fecha/Hora')
    before = models.JSONField(null=True, blank=True, verbose_name='Valores anteriores')
    after = models.JSONField(null=True, blank=True, verbose_name='Valores nuevos')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Dirección IP')

    class Meta:
        db_table = 'audit_log'
        ordering = ['-timestamp']
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'

    def __str__(self):
        return f'{self.get_action_display()} - {self.model_name} #{self.record_id} ({self.timestamp})'
