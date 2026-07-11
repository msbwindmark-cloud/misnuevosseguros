from django.contrib import admin
from .models import Poliza, PolizaEliminada, PolizaGarantia, PolizaGarantiaOption, PolizaGarantiaFranchise

admin.site.register(Poliza)
admin.site.register(PolizaEliminada)
admin.site.register(PolizaGarantia)
admin.site.register(PolizaGarantiaOption)
admin.site.register(PolizaGarantiaFranchise)
