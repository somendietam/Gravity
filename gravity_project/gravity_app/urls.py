from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path("register/", views.register, name="register"),
    path("accounts/login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("agregar-al-carrito/<int:producto_id>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("tu-carrito/", views.ver_carrito, name="tu_carrito"),  # Nueva ruta
    path("admin_panel/", views.admin_panel, name="admin_panel"),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('admin_panel/crear_producto/', views.crear_producto, name='crear_producto'),
    path('admin_panel/editar_producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),

]