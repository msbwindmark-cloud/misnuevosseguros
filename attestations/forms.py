from django import forms
from core.forms import BootstrapFormMixin
from .models import Attestation


class AttestationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Attestation
        fields = ['id_type_attestation', 'numero_attestation', 'seleccionado']
