from django import forms
from core.forms import BootstrapFormMixin
from .models import TipoDocumento


class TipoDocumentoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = TipoDocumento
        fields = '__all__'
