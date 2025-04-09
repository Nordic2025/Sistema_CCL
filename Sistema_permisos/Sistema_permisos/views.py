from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages # type: ignore
from django.http import HttpResponseForbidden



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def principal_view(request):
    ip_cliente = get_client_ip(request)
    clase_ip = 'ip_grande' if ip_cliente == '10.10.10.67' else ''
    print(f"IP detectada: {ip_cliente}") 
    return render(request, 'principal.html', {
        'ip_cliente': ip_cliente,
        'clase_ip': clase_ip
    })




