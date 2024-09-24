from django.contrib import admin
from .models import Producto, Categoria, CarritoCompras, Cliente, Pedido, PedidoProducto

admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(CarritoCompras)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(PedidoProducto)
