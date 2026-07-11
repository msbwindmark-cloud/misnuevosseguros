from django.contrib import admin
from .models import EnvioCourrier, Destinataire, Expediteur

admin.site.register(EnvioCourrier)
admin.site.register(Destinataire)
admin.site.register(Expediteur)
