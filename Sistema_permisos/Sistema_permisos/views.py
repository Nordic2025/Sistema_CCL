from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages # type: ignore


def principal_view(request):
    return render(request, 'principal.html')