from django import forms
from .models import Oferta
from core.forms import BootstrapFormMixin


class OfertaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Oferta
        fields = '__all__'
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehiculo_tipo'].queryset = self.fields['vehiculo_tipo'].queryset.filter(activo=True)
        self.fields['modalidad'].queryset = self.fields['modalidad'].queryset.filter(activo=True)
        self.fields['duracion'].queryset = self.fields['duracion'].queryset.filter(activo=True)
        self.fields['estado'].queryset = self.fields['estado'].queryset.filter(activo=True)
