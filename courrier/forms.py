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
        fields = '__all__'
