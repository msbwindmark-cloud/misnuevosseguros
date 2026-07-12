from django.contrib import admin
from .models import Oferta, TipoVehiculo, ModalidadSeguro, DuracionOferta, EstadoOferta

admin.site.register(Oferta)
admin.site.register(TipoVehiculo)
admin.site.register(ModalidadSeguro)
admin.site.register(DuracionOferta)
admin.site.register(EstadoOferta)
