from django.contrib import admin
from django import forms
from .models import Banco, Benificiario, EnvioBanco


class EnvioBancoAdminForm(forms.ModelForm):
    class Meta:
        model = EnvioBanco
        fields = '__all__'
        widgets = {
            'date_envoie': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.benificiario:
            instance.nom_envoie = instance.benificiario.nom_benificiaire
            instance.banque_envoie = instance.benificiario.banque_benificiaire
            instance.compte_envoie = instance.benificiario.compte_benificiaire
        if commit:
            instance.save()
            self.save_m2m()
        return instance


@admin.register(EnvioBanco)
class EnvioBancoAdmin(admin.ModelAdmin):
    form = EnvioBancoAdminForm
    list_display = ('id', 'nom_envoie', 'banque_envoie', 'compte_envoie', 'date_envoie', 'montant_envoie', 'benificiario', 'banco', 'nombre_documento_envoie_banque')
    list_display_links = ('id', 'nom_envoie')
    list_filter = ('date_envoie', 'banco', 'benificiario', 'tipo_documento_envoie_banque')
    search_fields = ('nom_envoie', 'banque_envoie', 'compte_envoie', 'motif_envoie', 'benificiario__nom_benificiaire', 'banco__nom_banque')
    readonly_fields = ('nom_envoie', 'banque_envoie', 'compte_envoie')
    ordering = ('-id',)
    list_per_page = 25
    fieldsets = (
        ('Virement', {
            'fields': ('banco', 'benificiario', 'date_envoie', 'montant_envoie', 'motif_envoie')
        }),
        ('Datos del beneficiario (auto-rellenados)', {
            'fields': ('nom_envoie', 'banque_envoie', 'compte_envoie')
        }),
        ('Documento', {
            'fields': ('tipo_documento_envoie_banque', 'nombre_documento_envoie_banque', 'tamanio_documento_envoie_banque'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Banco)
admin.site.register(Benificiario)
