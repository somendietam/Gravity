from django.contrib import admin
from .models import Categoria, Producto, CarritoCompras, Cliente, Pedido, PedidoProducto

admin.site.register(Categoria)
admin.site.register(CarritoCompras)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(PedidoProducto)
