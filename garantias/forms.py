from django import forms
from core.forms import BootstrapFormMixin
from .models import Garantia, GarantiaOption, GarantiaFranchise


class GarantiaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Garantia
        fields = ['nom_garantie', 'has_configuration']


class GarantiaOptionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GarantiaOption
        fields = ['nom_option', 'requires_montant']


class GarantiaFranchiseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GarantiaFranchise
        fields = ['nom_franchise']
