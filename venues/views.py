import json
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404
from .models import Espacio, Paquete, ServicioAdicional, FechaOcupada


def catalogo(request):
    tipo_filtro = request.GET.get('tipo', 'todos')
    capacidad_filtro = request.GET.get('capacidad', 'todas')

    espacios = Espacio.objects.filter(estado='publicado').order_by('orden')

    if tipo_filtro == 'interior':
        espacios = espacios.filter(tipo__startswith='interior')
    elif tipo_filtro == 'exterior':
        espacios = espacios.filter(tipo__startswith='exterior')
    elif tipo_filtro == 'mar':
        espacios = espacios.filter(tipo='exterior_cubierto')

    if capacidad_filtro == 'hasta200':
        espacios = espacios.filter(capacidad_max__lte=200)
    elif capacidad_filtro == '200_400':
        espacios = espacios.filter(capacidad_max__gt=200, capacidad_max__lte=400)
    elif capacidad_filtro == 'mas400':
        espacios = espacios.filter(capacidad_max__gt=400)

    tipo_opciones = [
        ('todos', 'Todos'),
        ('interior', 'Interior'),
        ('exterior', 'Exterior'),
        ('mar', 'Con vista al mar'),
    ]
    cap_opciones = [
        ('todas', 'Todas'),
        ('hasta200', 'Hasta 200'),
        ('200_400', '200 - 400'),
        ('mas400', '400+'),
    ]
    return render(request, 'venues/catalogo.html', {
        'espacios': espacios,
        'tipo_filtro': tipo_filtro,
        'capacidad_filtro': capacidad_filtro,
        'tipo_opciones': tipo_opciones,
        'cap_opciones': cap_opciones,
    })


def espacio_detail(request, slug):
    espacio = get_object_or_404(Espacio, slug=slug, estado='publicado')
    imagenes = espacio.imagenes.all()
    caracteristicas = espacio.caracteristicas.all()
    return render(request, 'venues/espacio_detail.html', {
        'espacio': espacio,
        'imagenes': imagenes,
        'caracteristicas': caracteristicas,
    })


def paquetes(request):
    paquetes_qs = Paquete.objects.all().prefetch_related('items')
    servicios = ServicioAdicional.objects.filter(activo=True)
    return render(request, 'venues/paquetes.html', {
        'paquetes': paquetes_qs,
        'servicios': servicios,
    })


def disponibilidad(request):
    espacios = Espacio.objects.filter(estado='publicado').order_by('orden')
    espacio_slug = request.GET.get('espacio', espacios.first().slug if espacios.exists() else '')
    espacio_sel = get_object_or_404(Espacio, slug=espacio_slug) if espacio_slug else None

    hoy = date.today()
    year = int(request.GET.get('year', hoy.year))
    month = int(request.GET.get('month', hoy.month))

    # Build calendar data
    primer_dia = date(year, month, 1)
    if month == 12:
        ultimo_dia = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(year, month + 1, 1) - timedelta(days=1)

    fechas_ocupadas_set = set()
    if espacio_sel:
        fechas_ocupadas_set = set(
            FechaOcupada.objects.filter(
                espacio=espacio_sel,
                fecha__year=year,
                fecha__month=month,
            ).values_list('fecha', flat=True)
        )

    # Mes anterior / siguiente
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    dias_calendario = []
    # Fill blanks before first day (Monday=0)
    offset = primer_dia.weekday()
    for _ in range(offset):
        dias_calendario.append(None)
    current = primer_dia
    while current <= ultimo_dia:
        dias_calendario.append({
            'date': current,
            'ocupado': current in fechas_ocupadas_set,
            'es_hoy': current == hoy,
            'pasado': current < hoy,
        })
        current += timedelta(days=1)

    return render(request, 'venues/disponibilidad.html', {
        'espacios': espacios,
        'espacio_sel': espacio_sel,
        'dias_calendario': dias_calendario,
        'year': year,
        'month': month,
        'month_nombre': primer_dia.strftime('%B %Y').capitalize(),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    })