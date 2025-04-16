from django import forms
from .models import Administrador, Areas, Curso, Inspector
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class AdministradorForm(forms.ModelForm):

    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Requerido. Al menos 8 caracteres y no puede ser completamente numérico.',
    )

    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Ingrese la misma contraseña que antes, para verificación.',
    )


    class Meta:
        model = Administrador
        fields = ['rut', 'nombre', 'area', 'password1', 'password2']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if User.objects.filter(username=rut).exists():
            raise forms.ValidationError("Ya existe un administrador con el mismo RUT")
        return rut
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        
        return cleaned_data
    

# Formulario para editar administrador (sin cambiar contraseña)
class AdministradorEditForm(forms.ModelForm):
   
    class Meta:
        model = Administrador
        fields = ['nombre', 'area']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
        }
    

# Formulario para cambiar contraseña
class CambiarPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        
        return cleaned_data



class AreasForm(forms.ModelForm):
    class Meta:
        model = Areas
        fields = ['nombre', 'encargado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'encargado': forms.TextInput(attrs={'class': 'form-control'}),
        }

#CURSOS FORM

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

#INSPECTORES FORM

class InspectorForm(forms.ModelForm):
    class Meta:
        model = Inspector
        fields = ['nombre', 'rut', 'telefono', 'cursos']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56912345678'}),
            'cursos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }