from django.db import models


class TipoDocumento(models.Model):
    tipo_documento = models.CharField(max_length=255, verbose_name='Tipo de documento')
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tipo_documentos'
        verbose_name = 'Tipo de documento'
        verbose_name_plural = 'Tipos de documentos'

    def __str__(self):
        return self.tipo_documento


class DocumentoUsuario(models.Model):
    id_usuario = models.IntegerField(verbose_name='ID Usuario')
    tipo_documento_usuario = models.CharField(max_length=255, blank=True, default='')
    nombre_documento_usuario = models.CharField(max_length=255, blank=True, default='')
    tamanio_documento_usuario = models.BigIntegerField(blank=True, null=True)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.SET_NULL, null=True, blank=True)
    archivo = models.FileField(upload_to='documentos_usuarios/', blank=True)
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documentos_usuarios'
        verbose_name = 'Documento de usuario'
        verbose_name_plural = 'Documentos de usuarios'

    def __str__(self):
        return self.nombre_documento_usuario or ''
