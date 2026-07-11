from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['code_client', 'nom_client', 'telephone_client', 'email_client']
        widgets = {
            'code_client': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_client': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone_client': forms.TextInput(attrs={'class': 'form-control'}),
            'email_client': forms.EmailInput(attrs={'class': 'form-control'}),
        }
