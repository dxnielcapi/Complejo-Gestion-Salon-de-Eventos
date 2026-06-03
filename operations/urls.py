from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('agenda/', views.agenda, name='agenda'),
    path('reservas/', views.reservas_lista, name='reservas_lista'),
    path('reservas/<str:codigo>/', views.reservas_detalle, name='reservas_detalle'),
    path('catalogo/', views.catalogo_ops, name='catalogo'),
    path('reportes/', views.reportes, name='reportes'),
]
