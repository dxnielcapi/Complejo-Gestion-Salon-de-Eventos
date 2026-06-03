from django.urls import path
from . import views

app_name = 'venues'

urlpatterns = [
    path('espacios/', views.catalogo, name='catalogo'),
    path('espacios/<slug:slug>/', views.espacio_detail, name='espacio_detail'),
    path('paquetes/', views.paquetes, name='paquetes'),
    path('disponibilidad/', views.disponibilidad, name='disponibilidad'),
]
