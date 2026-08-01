from django.contrib import admin
from django import forms
from .models import EnvioCourrier, Destinataire, Expediteur


class EnvioCourrierAdminForm(forms.ModelForm):
    class Meta:
        model = EnvioCourrier
        fields = '__all__'
        widgets = {
            'date_envoie_courrier': forms.DateInput(attrs={'type': 'date'}),
        }


@admin.register(EnvioCourrier)
class EnvioCourrierAdmin(admin.ModelAdmin):
    form = EnvioCourrierAdminForm
    list_display = ('id', 'date_envoie_courrier', 'expediteur_envoie_courrier', 'destinataire_envoie_courrier', 'addresse_envoie_courrier', 'nombre_documento_envoie_courrier')
    list_display_links = ('id', 'date_envoie_courrier')
    list_filter = ('date_envoie_courrier', 'tipo_documento_envoie_courrier')
    search_fields = ('expediteur_envoie_courrier', 'destinataire_envoie_courrier', 'addresse_envoie_courrier', 'nombre_documento_envoie_courrier')
    ordering = ('-id',)
    list_per_page = 25
    fieldsets = (
        ('Envoie Courrier', {
            'fields': ('date_envoie_courrier', 'expediteur_envoie_courrier', 'addresse_expediteur_envoie_courrier', 'destinataire_envoie_courrier', 'addresse_envoie_courrier')
        }),
        ('Documento', {
            'fields': ('tipo_documento_envoie_courrier', 'nombre_documento_envoie_courrier', 'tamanio_documento_envoie_courrier'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Destinataire)
class DestinataireAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom_destinataire', 'adresse_destinataire')
    list_display_links = ('id', 'nom_destinataire')
    search_fields = ('nom_destinataire',)
    ordering = ('-id',)


@admin.register(Expediteur)
class ExpediteurAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom_expediteur', 'adresse_expediteur')
    list_display_links = ('id', 'nom_expediteur')
    search_fields = ('nom_expediteur',)
    ordering = ('-id',)
