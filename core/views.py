from django.shortcuts import render
from venues.models import Espacio, Paquete, ServicioAdicional


def home(request):
    espacios = Espacio.objects.filter(estado='publicado').order_by('orden')[:4]
    paquetes = Paquete.objects.all().prefetch_related('items')
    context = {
        'espacios': espacios,
        'paquetes': paquetes,
    }
    return render(request, 'core/home.html', context)
