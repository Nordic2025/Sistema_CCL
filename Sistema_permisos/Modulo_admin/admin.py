from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Administrador, Areas

# Personalizar la visualización de Administrador en el panel de admin
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'area', 'get_username')
    search_fields = ('rut', 'nombre', 'area')
    list_filter = ('area',)
    
    def get_username(self, obj):
        return obj.user.username if obj.user else "Sin usuario"
    get_username.short_description = 'Usuario'

# Personalizar la visualización de Areas en el panel de admin
class AreasAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'encargado')
    search_fields = ('nombre', 'encargado')

# Registrar los modelos
admin.site.register(Administrador, AdministradorAdmin)
admin.site.register(Areas, AreasAdmin)
