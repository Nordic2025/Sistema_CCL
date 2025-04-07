from django import forms
from .models import RegistroSalida
from Modulo_admin.models import Areas

class Modulo_funcionariosForm(forms.ModelForm):
    # Creamos un campo personalizado para mostrar los encargados
    autorizado_por = forms.ModelChoiceField(
        queryset=Areas.objects.all(),
        label="Autorizado por",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_autorizado_por'}),
        # Personalizamos cómo se muestra cada opción
        to_field_name="id",  # Usamos el ID como valor
        empty_label="Seleccione un encargado"
    )
    
    class Meta:
        model = RegistroSalida
        fields = ['rut', 'nombre', 'autorizado_por', 'area_perteneciente', 'motivo_salida']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre completo'}),
            'area_perteneciente': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'id': 'id_area_perteneciente'}),
            'motivo_salida': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizamos las etiquetas que se muestran en el desplegable
        self.fields['autorizado_por'].label_from_instance = lambda obj: f"{obj.encargado}"
        self.fields['area_perteneciente'].required = False
