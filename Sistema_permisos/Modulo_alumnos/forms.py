from django import forms
from .models import RegistroRetiro, RegistroJustificativo

class RegistroRetiroForm(forms.ModelForm):
    class Meta:
        model = RegistroRetiro
        fields = ['rut_persona_retira', 'rut_estudiante', 'nombre_estudiante', 
                  'curso', 'inspector_cargo', 'motivo_retiro']
        widgets = {
            'rut_persona_retira': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12.345.678-9'
            }),
            'rut_estudiante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12.345.678-9'
            }),
            'nombre_estudiante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del estudiante'
            }),
            'curso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 3° Básico A'
            }),
            'inspector_cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del inspector'
            }),
            'motivo_retiro': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class RegistroJustificativoForm(forms.ModelForm):
    class Meta:
        model = RegistroJustificativo
        fields = ['rut_persona_justifica', 'rut_estudiante', 'nombre_estudiante', 
                  'curso', 'hora_llegada']
        widgets = {
            'rut_persona_justifica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12.345.678-9'
            }),
            'rut_estudiante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12.345.678-9'
            }),
            'nombre_estudiante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del estudiante'
            }),
            'curso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 3° Básico A'
            }),
            'hora_llegada': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hora de llegada'
            }),

        }

