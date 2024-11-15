from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="index"),
    path("register/", views.register, name="register"),
    path("accounts/login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("agregar-al-carrito/<int:producto_id>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("eliminar-del-carrito/<int:producto_id>/", views.eliminar_del_carrito, name="eliminar_del_carrito"),
    path("tu-carrito/", views.ver_carrito, name="tu_carrito"),  # Nueva ruta
    path("admin_panel/", views.admin_panel, name="admin_panel"),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pagar-pedido/', views.pagar_pedido, name='pagar_pedido'),
    path('pedido/<int:pedido_id>/factura/', views.generar_factura, name='generar_factura'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('admin_panel/crear_producto/', views.crear_producto, name='crear_producto'),
    path('admin_panel/editar_producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('crear_categoria/', views.crear_categoria, name='crear_categoria'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('api/productos-en-stock/', views.productos_en_stock, name='productos_en_stock'),
    path('ai_clothes_suggestion/', views.ai_clothes_suggestion, name='ai_clothes_suggestion'),
]