from django import forms
from .models import Administrador, Areas, Curso, Alumno, Inspector
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re

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

#Formulario de alumno
class AlumnoForm(forms.ModelForm):

    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        empty_label="Seleccione un curso",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Alumno
        fields = ['rut', 'nombre', 'curso', 'apoderado_titular', 'rut_apoderadoT', 'telefono_apoderadoT', 
                 'apoderado_suplente', 'rut_apoderadoS', 'telefono_apoderadoS']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control rut-input', 'placeholder': 'Ej: 12.345.678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'apoderado_titular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del apoderado titular'}),
            'rut_apoderadoT': forms.TextInput(attrs={'class': 'form-control rut-input', 'placeholder': 'Rut del apoderado titular'}),
            'telefono_apoderadoT': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del apoderado titular'}),
            'apoderado_suplente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del apoderado suplente'}),
            'rut_apoderadoS': forms.TextInput(attrs={'class': 'form-control rut-input', 'placeholder': 'Rut del apoderado suplente'}),
            'telefono_apoderadoS': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del apoderado suplente'}),
        }
        
    def clean_rut(self):
        """Validar formato y dígito verificador del RUT."""
        rut = self.cleaned_data.get('rut')
        
        # Eliminar puntos y guión para validar
        rut_limpio = re.sub(r'[^0-9kK]', '', rut)
        
        if len(rut_limpio) < 2:
            raise forms.ValidationError('El RUT ingresado no es válido.')
            
        # Separar cuerpo y dígito verificador
        cuerpo, dv = rut_limpio[:-1], rut_limpio[-1].upper()
        
        # Calcular dígito verificador
        suma = 0
        multiplo = 2
        
        for r in reversed(cuerpo):
            suma += int(r) * multiplo
            multiplo = 2 if multiplo == 7 else multiplo + 1
            
        resto = suma % 11
        dv_calculado = '0' if resto == 0 else 'K' if resto == 1 else str(11 - resto)
        
        if dv != dv_calculado:
            raise forms.ValidationError('El RUT ingresado tiene un dígito verificador incorrecto.')
            
        # Formatear RUT para guardar
        rut_formateado = f"{cuerpo[:-6]}.{cuerpo[-6:-3]}.{cuerpo[-3:]}-{dv}" if len(cuerpo) > 6 else f"{cuerpo}-{dv}"
        
        return rut_formateado

class FamiliarForm(forms.Form):
    familiar_nombre = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del familiar'})
    )
    familiar_rut = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={'class': 'form-control rut-input', 'placeholder': 'Rut del familiar'})
    )
    familiar_relacion = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tío, Abuelo, etc.'})
    )
    familiar_telefono = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono de contacto'})
    )
    
    def clean_familiar_telefono(self):
        """Validar formato del teléfono."""
        telefono = self.cleaned_data.get('familiar_telefono')
        
        # Eliminar espacios y caracteres no numéricos
        telefono_limpio = re.sub(r'[^0-9+]', '', telefono)
        
        if len(telefono_limpio) < 8:
            raise forms.ValidationError('El número de teléfono debe tener al menos 8 dígitos.')
            
        return telefono_limpio



# Formulario de curso
class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'nivel']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
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