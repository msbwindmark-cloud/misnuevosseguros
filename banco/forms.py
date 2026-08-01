from django import forms
from core.forms import BootstrapFormMixin
from .models import Banco, Benificiario, EnvioBanco


class BancoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Banco
        fields = '__all__'


class BenificiarioForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Benificiario
        fields = '__all__'


class EnvioBancoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = EnvioBanco
        fields = ['banco', 'benificiario', 'date_envoie', 'montant_envoie', 'motif_envoie']
        widgets = {
            'date_envoie': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
