from django.db import models


class TipoVehiculo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'ofertas_tipo_vehiculo'
        verbose_name = 'Tipo de Vehículo'
        verbose_name_plural = 'Tipos de Vehículos'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class ModalidadSeguro(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, default='')
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'ofertas_modalidad_seguro'
        verbose_name = 'Modalidad de Seguro'
        verbose_name_plural = 'Modalidades de Seguro'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class DuracionOferta(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    meses = models.PositiveIntegerField(help_text='Duración en meses')
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'ofertas_duracion'
        verbose_name = 'Duración de Oferta'
        verbose_name_plural = 'Duraciones de Oferta'
        ordering = ['orden', 'meses']

    def __str__(self):
        return self.nombre


class EstadoOferta(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=20, default='secondary', help_text='Color Bootstrap (primary, success, danger, etc.)')
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'ofertas_estado'
        verbose_name = 'Estado de Oferta'
        verbose_name_plural = 'Estados de Oferta'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class Oferta(models.Model):
    cliente_nombre = models.CharField(max_length=200, verbose_name='Nombre del cliente')
    cliente_telefono = models.CharField(max_length=50, blank=True, default='', verbose_name='Teléfono')
    cliente_email = models.EmailField(blank=True, default='', verbose_name='Email')

    vehiculo_tipo = models.ForeignKey(TipoVehiculo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Tipo de vehículo')
    vehiculo_marca = models.CharField(max_length=100, blank=True, default='', verbose_name='Marca')
    vehiculo_modelo = models.CharField(max_length=100, blank=True, default='', verbose_name='Modelo')
    vehiculo_matricula = models.CharField(max_length=50, blank=True, default='', verbose_name='Matrícula')
    vehiculo_potencia = models.CharField(max_length=50, blank=True, default='', verbose_name='Potencia / Cilindrada')
    vehiculo_anio = models.PositiveIntegerField(blank=True, null=True, verbose_name='Año')

    modalidad = models.ForeignKey(ModalidadSeguro, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Modalidad')
    duracion = models.ForeignKey(DuracionOferta, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Duración')

    prima_estimada = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Prima estimada')
    notas = models.TextField(blank=True, default='', verbose_name='Notas / Observaciones')

    estado = models.ForeignKey(EstadoOferta, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Estado')
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    modificado_el = models.DateTimeField(auto_now=True, verbose_name='Modificado el')

    class Meta:
        db_table = 'ofertas'
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
        ordering = ['-creado_el']

    def __str__(self):
        estado = self.estado.nombre if self.estado else 'Sin estado'
        return f'Oferta {self.id} - {self.cliente_nombre} ({estado})'

    @property
    def vehiculo_completo(self):
        parts = []
        if self.vehiculo_tipo:
            parts.append(self.vehiculo_tipo.nombre)
        if self.vehiculo_marca:
            parts.append(self.vehiculo_marca)
        if self.vehiculo_modelo:
            parts.append(self.vehiculo_modelo)
        return ' '.join(parts) if parts else '—'
