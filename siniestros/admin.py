from django.contrib import admin
from .models import Sinistro, DocumentoSinistro, Formule, ReferenceReglement, DocumentDeBase

admin.site.register(Sinistro)
admin.site.register(DocumentoSinistro)
admin.site.register(Formule)
admin.site.register(ReferenceReglement)
admin.site.register(DocumentDeBase)
