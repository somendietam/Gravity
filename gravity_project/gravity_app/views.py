from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Producto, CarritoCompras, Cliente

def index(request):
    context = {}
    return render(request, 'gravity_app/index.html', context)



