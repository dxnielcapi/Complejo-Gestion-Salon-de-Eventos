from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('cotizar/', views.paso_1, name='paso_1'),
    path('cotizar/espacio/', views.paso_2, name='paso_2'),
    path('cotizar/fecha/', views.paso_3, name='paso_3'),
    path('cotizar/paquete/', views.paso_4, name='paso_4'),
    path('cotizar/extras/', views.paso_5, name='paso_5'),
    path('cotizar/datos/', views.paso_6, name='paso_6'),
    path('cotizar/pago/', views.paso_7, name='paso_7'),
    path('cotizar/confirmacion/<str:codigo>/', views.confirmacion, name='confirmacion'),
    path('portal/reservas/', views.mis_reservas, name='mis_reservas'),
    path('portal/reservas/<str:codigo>/', views.detalle_cliente, name='detalle_cliente'),
]
