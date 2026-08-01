from django import forms
from core.forms import BootstrapFormMixin
from .models import Destinataire, Expediteur, EnvioCourrier


class DestinataireForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Destinataire
        fields = '__all__'


class ExpediteurForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Expediteur
        fields = '__all__'


class EnvioCourrierForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = EnvioCourrier
        fields = ['date_envoie_courrier', 'addresse_expediteur_envoie_courrier', 'addresse_envoie_courrier']
        widgets = {
            'date_envoie_courrier': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'addresse_expediteur_envoie_courrier': forms.Textarea(attrs={'rows': 3}),
            'addresse_envoie_courrier': forms.Textarea(attrs={'rows': 3}),
        }
