from django import forms
from .models import RegistroRetiro

class RegistroRetiroForm(forms.ModelForm):
    class Meta:
        model = RegistroRetiro
        fields = [
            'rut_persona_retira',
            'nombre_persona_retira',
            'rut_estudiante',
            'nombre_estudiante',
            'curso',
            'inspector_cargo',
            'motivo_retiro'
        ]
        widgets = {
            'rut_persona_retira': forms.HiddenInput(),  # Este campo se llena automáticamente
            'nombre_persona_retira': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), 
            'rut_estudiante': forms.Select(attrs={'class': 'form-select'}),
            'nombre_estudiante': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'curso': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'inspector_cargo': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'motivo_retiro': forms.Select(attrs={'class': 'form-select'}),
        }
