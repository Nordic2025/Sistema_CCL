from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def duration_seconds(value):
    """Convierte un objeto timedelta a una representación en segundos enteros"""
    if isinstance(value, timedelta):
        # Redondear a segundos enteros
        total_seconds = round(value.total_seconds())
        
        # Formatear como horas, minutos y segundos
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        result = ""
        if hours > 0:
            result += f"{hours}h "
        if minutes > 0 or hours > 0:
            result += f"{minutes}m "
        result += f"{seconds}s"
        
        return result
    return value
