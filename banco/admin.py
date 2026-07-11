from django.contrib import admin
from .models import Banco, Benificiario, EnvioBanco

admin.site.register(Banco)
admin.site.register(Benificiario)
admin.site.register(EnvioBanco)
