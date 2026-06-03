from datetime import date
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from venues.models import Espacio, Paquete, ServicioAdicional, FechaOcupada
from .models import Reserva, ReservaServicio, ActividadReserva
from .forms import Paso1Form, Paso2Form, Paso3Form, Paso4Form, Paso5Form, Paso6Form, Paso7Form


# ──────────────────────────────────────────────────────────────
#  WIZARD HELPERS
# ──────────────────────────────────────────────────────────────

WIZARD_KEY = 'cotizador'
TOTAL_PASOS = 7


def _get_wizard_data(request):
    return request.session.get(WIZARD_KEY, {})


def _save_wizard_data(request, data):
    request.session[WIZARD_KEY] = data
    request.session.modified = True


def _calcular_total(data):
    try:
        espacio = Espacio.objects.get(pk=data.get('espacio_id'))
        paquete = Paquete.objects.get(pk=data.get('paquete_id'))
        num = int(data.get('num_invitados', 0))
        base = Decimal(str(espacio.precio_base))
        paquete_total = paquete.precio_por_persona * num
        extras = Decimal('0')
        for sid in data.get('servicios_ids', []):
            try:
                s = ServicioAdicional.objects.get(pk=sid)
                if s.precio_tipo == 'por_persona':
                    extras += s.precio * num
                else:
                    extras += s.precio
            except ServicioAdicional.DoesNotExist:
                pass
        total = base + paquete_total + extras
        return {
            'renta_espacio': base,
            'paquete_subtotal': paquete_total,
            'extras_subtotal': extras,
            'total': total,
            'anticipo': (total * Decimal('0.25')).quantize(Decimal('1')),
        }
    except (Espacio.DoesNotExist, Paquete.DoesNotExist, Exception):
        return {}


def _cotizacion_context(data):
    ctx = {'wizard_data': data}
    ctx.update(_calcular_total(data))
    try:
        ctx['espacio_obj'] = Espacio.objects.get(pk=data['espacio_id'])
    except (KeyError, Espacio.DoesNotExist):
        pass
    try:
        ctx['paquete_obj'] = Paquete.objects.get(pk=data['paquete_id'])
    except (KeyError, Paquete.DoesNotExist):
        pass
    return ctx


# ──────────────────────────────────────────────────────────────
#  PASOS
# ──────────────────────────────────────────────────────────────

def paso_1(request):
    data = _get_wizard_data(request)
    if request.method == 'POST':
        form = Paso1Form(request.POST)
        if form.is_valid():
            data.update({
                'tipo_evento': form.cleaned_data['tipo_evento'],
                'num_invitados': form.cleaned_data['num_invitados'],
                'hora_inicio': str(form.cleaned_data['hora_inicio']),
            })
            _save_wizard_data(request, data)
            return redirect('bookings:paso_2')
    else:
        form = Paso1Form(initial=data)
    return render(request, 'bookings/wizard/paso_1.html', {
        'form': form, 'paso': 1, **_cotizacion_context(data)
    })


def paso_2(request):
    data = _get_wizard_data(request)
    espacios = Espacio.objects.filter(estado='publicado').order_by('orden')
    if request.method == 'POST':
        espacio_id = request.POST.get('espacio_id')
        if espacio_id:
            data['espacio_id'] = int(espacio_id)
            _save_wizard_data(request, data)
            return redirect('bookings:paso_3')
    return render(request, 'bookings/wizard/paso_2.html', {
        'espacios': espacios, 'paso': 2, **_cotizacion_context(data)
    })


def paso_3(request):
    data = _get_wizard_data(request)
    espacio_id = data.get('espacio_id')
    fechas_ocupadas = []
    if espacio_id:
        fechas_ocupadas = list(
            FechaOcupada.objects.filter(espacio_id=espacio_id)
            .values_list('fecha', flat=True)
        )
        fechas_ocupadas = [str(f) for f in fechas_ocupadas]

    if request.method == 'POST':
        form = Paso3Form(request.POST)
        if form.is_valid():
            data['fecha'] = str(form.cleaned_data['fecha'])
            _save_wizard_data(request, data)
            return redirect('bookings:paso_4')
    else:
        form = Paso3Form(initial={'fecha': data.get('fecha')})
    return render(request, 'bookings/wizard/paso_3.html', {
        'form': form, 'paso': 3,
        'fechas_ocupadas_json': fechas_ocupadas,
        **_cotizacion_context(data),
    })


def paso_4(request):
    data = _get_wizard_data(request)
    paquetes = Paquete.objects.all().prefetch_related('items')
    if request.method == 'POST':
        paquete_id = request.POST.get('paquete_id')
        if paquete_id:
            data['paquete_id'] = int(paquete_id)
            _save_wizard_data(request, data)
            return redirect('bookings:paso_5')
    return render(request, 'bookings/wizard/paso_4.html', {
        'paquetes': paquetes, 'paso': 4, **_cotizacion_context(data)
    })


def paso_5(request):
    data = _get_wizard_data(request)
    servicios = ServicioAdicional.objects.filter(activo=True)
    if request.method == 'POST':
        form = Paso5Form(request.POST)
        if form.is_valid():
            data['servicios_ids'] = [s.pk for s in form.cleaned_data['servicios']]
            _save_wizard_data(request, data)
            return redirect('bookings:paso_6')
    else:
        sel_ids = data.get('servicios_ids', [])
        form = Paso5Form(initial={'servicios': ServicioAdicional.objects.filter(pk__in=sel_ids)})
    return render(request, 'bookings/wizard/paso_5.html', {
        'form': form, 'servicios': servicios, 'paso': 5, **_cotizacion_context(data)
    })


def paso_6(request):
    data = _get_wizard_data(request)
    if request.method == 'POST':
        form = Paso6Form(request.POST)
        if form.is_valid():
            data.update({
                'nombre': form.cleaned_data['nombre'],
                'apellidos': form.cleaned_data['apellidos'],
                'email': form.cleaned_data['email'],
                'telefono': form.cleaned_data['telefono'],
            })
            _save_wizard_data(request, data)
            return redirect('bookings:paso_7')
    else:
        form = Paso6Form(initial=data)
    return render(request, 'bookings/wizard/paso_6.html', {
        'form': form, 'paso': 6, **_cotizacion_context(data)
    })


def paso_7(request):
    data = _get_wizard_data(request)
    totales = _calcular_total(data)
    if request.method == 'POST':
        form = Paso7Form(request.POST)
        if form.is_valid():
            reserva = _crear_reserva(request, data, totales)
            if reserva:
                del request.session[WIZARD_KEY]
                return redirect('bookings:confirmacion', codigo=reserva.codigo)
            messages.error(request, 'Hubo un error al procesar tu reserva. Intenta de nuevo.')
    else:
        form = Paso7Form()
    return render(request, 'bookings/wizard/paso_7.html', {
        'form': form, 'paso': 7,
        **_cotizacion_context(data),
        **totales,
    })


def _crear_reserva(request, data, totales):
    try:
        email = data['email']
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': data.get('nombre', ''),
                'last_name': data.get('apellidos', ''),
            }
        )
        if created:
            user.set_unusable_password()
            user.save()

        from accounts.models import ClienteProfile
        ClienteProfile.objects.get_or_create(
            user=user,
            defaults={'telefono': data.get('telefono', '')}
        )

        reserva = Reserva.objects.create(
            cliente=user,
            espacio=Espacio.objects.get(pk=data['espacio_id']),
            paquete=Paquete.objects.get(pk=data['paquete_id']),
            tipo_evento=data['tipo_evento'],
            fecha=data['fecha'],
            hora_inicio=data['hora_inicio'],
            num_invitados=data['num_invitados'],
            total_evento=totales.get('total', 0),
            anticipo_pagado=totales.get('anticipo', 0),
            estado='confirmada',
        )

        for sid in data.get('servicios_ids', []):
            try:
                ReservaServicio.objects.create(
                    reserva=reserva,
                    servicio=ServicioAdicional.objects.get(pk=sid),
                )
            except ServicioAdicional.DoesNotExist:
                pass

        # Marcar fecha como ocupada
        FechaOcupada.objects.get_or_create(
            espacio=reserva.espacio,
            fecha=reserva.fecha,
            defaults={'motivo': 'reserva'}
        )

        ActividadReserva.objects.create(
            reserva=reserva,
            descripcion='Reserva creada · Anticipo del 25% recibido',
        )
        return reserva
    except Exception:
        return None


def confirmacion(request, codigo):
    reserva = get_object_or_404(Reserva, codigo=codigo)
    return render(request, 'bookings/confirmacion.html', {'reserva': reserva})


# ──────────────────────────────────────────────────────────────
#  PORTAL CLIENTE
# ──────────────────────────────────────────────────────────────

@login_required
def mis_reservas(request):
    estado_filtro = request.GET.get('estado', 'todas')
    reservas = Reserva.objects.filter(cliente=request.user).order_by('-fecha')
    if estado_filtro != 'todas':
        reservas = reservas.filter(estado=estado_filtro)

    activas = Reserva.objects.filter(cliente=request.user, estado__in=['confirmada', 'pendiente_liquidacion']).count()
    total_invertido = sum(
        r.anticipo_pagado for r in Reserva.objects.filter(cliente=request.user)
    )
    proxima = Reserva.objects.filter(
        cliente=request.user, fecha__gte=date.today(),
        estado__in=['confirmada', 'pendiente_liquidacion']
    ).order_by('fecha').first()

    filtros = [
        ('todas', 'Todas'),
        ('confirmada', 'Confirmada'),
        ('pendiente_liquidacion', 'Pendiente liquidación'),
        ('completada', 'Completada'),
    ]
    return render(request, 'portal/mis_reservas.html', {
        'reservas': reservas,
        'estado_filtro': estado_filtro,
        'activas': activas,
        'total_invertido': total_invertido,
        'proxima': proxima,
        'filtros': filtros,
    })


@login_required
def detalle_cliente(request, codigo):
    reserva = get_object_or_404(Reserva, codigo=codigo, cliente=request.user)
    return render(request, 'portal/detalle_cliente.html', {'reserva': reserva})
