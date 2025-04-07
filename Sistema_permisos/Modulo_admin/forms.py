from django import forms
from .models import Administrador, Areas

class AdministradorForm(forms.ModelForm):
    class Meta:
        model = Administrador
        fields = ['rut', 'nombre', 'area']


class AreasForm(forms.ModelForm):
    class Meta:
        model = Areas
        fields = ['nombre', 'encargado']
        

