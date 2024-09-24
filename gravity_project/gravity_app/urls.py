from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),  
    path("admin_panel/", views.admin_panel, name="admin_panel"),
]