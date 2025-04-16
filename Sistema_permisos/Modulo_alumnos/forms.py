from django import forms
from .models import RegistroRetiro

class RegistroRetiroForm(forms.ModelForm):
    class Meta:
        model = RegistroRetiro
        fields = [
            'rut_persona_retira', 
            'tipo_persona', 
            'rut_estudiante', 
            'nombre_estudiante', 
            'curso', 
            'inspector_cargo', 
            'motivo_retiro'
        ]
        widgets = {
            'rut_persona_retira': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_persona': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'rut_estudiante': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_estudiante': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'curso': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'inspector_cargo': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'motivo_retiro': forms.Select(attrs={'class': 'form-select'}),
        }
