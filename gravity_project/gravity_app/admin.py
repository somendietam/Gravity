from django.contrib import admin
from .models import Producto, Categoria, CarritoCompras, Cliente, Pedido, PedidoProducto
from .forms import ProductoForm

# Personalizamos la interfaz para gestionar las categorías
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']  # Los campos que se mostrarán en la lista de categorías
    search_fields = ['nombre']  # Permitir buscar categorías por nombre

class ProductoAdmin(admin.ModelAdmin):
    form = ProductoForm
    list_display = ['nombre', 'precio', 'stock', 'categoria']  # Mostrar columnas en la lista de productos
    
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(CarritoCompras)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(PedidoProducto)
