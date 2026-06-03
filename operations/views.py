from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q

from bookings.models import Reserva, PagoRegistro, ActividadReserva
from venues.models import Espacio, Paquete, ServicioAdicional, FechaOcupada
from .models import TareaPendiente


@staff_member_required(login_url='/accounts/login/')
def dashboard(request):
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year

    reservas_mes = Reserva.objects.filter(fecha__year=anio_actual, fecha__month=mes_actual)
    eventos_mes = reservas_mes.count()
    ingresos_confirmados = reservas_mes.filter(
        estado__in=['confirmada', 'completada']
    ).aggregate(total=Sum('total_evento'))['total'] or Decimal('0')
    pipeline_total = Reserva.objects.filter(
        estado__in=['confirmada', 'pendiente_liquidacion']
    ).aggregate(total=Sum('total_evento'))['total'] or Decimal('0')
    tasa_ocupacion = 72  # Calculado de ejemplo

    proximos = Reserva.objects.filter(
        fecha__gte=hoy
    ).select_related('cliente', 'espacio', 'paquete').order_by('fecha')[:8]

    ocupacion_por_espacio = []
    for esp in Espacio.objects.filter(estado='publicado').order_by('orden'):
        count = Reserva.objects.filter(
            espacio=esp,
            fecha__year=anio_actual,
            fecha__month=mes_actual,
        ).count()
        ocupacion_por_espacio.append({'espacio': esp, 'count': count})

    tareas = TareaPendiente.objects.filter(completada=False).order_by('-prioridad')[:5]
    reservas_liquidar = Reserva.objects.filter(
        estado='pendiente_liquidacion',
        fecha__lte=hoy + timedelta(days=7)
    ).count()

    return render(request, 'operations/dashboard.html', {
        'hoy': hoy,
        'eventos_mes': eventos_mes,
        'ingresos_confirmados': ingresos_confirmados,
        'pipeline_total': pipeline_total,
        'tasa_ocupacion': tasa_ocupacion,
        'proximos': proximos,
        'ocupacion_por_espacio': ocupacion_por_espacio,
        'tareas': tareas,
        'reservas_liquidar': reservas_liquidar,
    })


@staff_member_required(login_url='/accounts/login/')
def agenda(request):
    hoy = date.today()
    year = int(request.GET.get('year', hoy.year))
    month = int(request.GET.get('month', hoy.month))
    espacio_filtro = request.GET.get('espacio', '')

    primer_dia = date(year, month, 1)
    if month == 12:
        ultimo_dia = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(year, month + 1, 1) - timedelta(days=1)

    reservas_mes = Reserva.objects.filter(
        fecha__year=year, fecha__month=month
    ).select_related('espacio', 'cliente')
    if espacio_filtro:
        reservas_mes = reservas_mes.filter(espacio__slug=espacio_filtro)

    reservas_por_fecha = {}
    for r in reservas_mes:
        reservas_por_fecha.setdefault(r.fecha, []).append(r)

    dias_calendario = []
    offset = primer_dia.weekday()
    for _ in range(offset):
        dias_calendario.append(None)
    current = primer_dia
    while current <= ultimo_dia:
        dias_calendario.append({
            'date': current,
            'reservas': reservas_por_fecha.get(current, []),
            'es_hoy': current == hoy,
        })
        current += timedelta(days=1)

    dia_sel_str = request.GET.get('dia', '')
    dia_sel = None
    reservas_dia = []
    if dia_sel_str:
        try:
            dia_sel = date.fromisoformat(dia_sel_str)
            reservas_dia = reservas_por_fecha.get(dia_sel, [])
        except ValueError:
            pass

    # Resumen del mes
    total_invitados = sum(r.num_invitados for r in reservas_mes)
    ingreso_esperado = reservas_mes.aggregate(t=Sum('total_evento'))['t'] or 0
    dias_ocupados = len(reservas_por_fecha)

    if month == 1:
        prev_m, prev_y = 12, year - 1
    else:
        prev_m, prev_y = month - 1, year
    if month == 12:
        next_m, next_y = 1, year + 1
    else:
        next_m, next_y = month + 1, year

    return render(request, 'operations/agenda.html', {
        'dias_calendario': dias_calendario,
        'year': year,
        'month': month,
        'month_nombre': primer_dia.strftime('%B %Y').capitalize(),
        'prev_year': prev_y, 'prev_month': prev_m,
        'next_year': next_y, 'next_month': next_m,
        'dia_sel': dia_sel,
        'reservas_dia': reservas_dia,
        'eventos_mes': reservas_mes.count(),
        'total_invitados': total_invitados,
        'ingreso_esperado': ingreso_esperado,
        'dias_ocupados': dias_ocupados,
        'espacios': Espacio.objects.filter(estado='publicado'),
        'espacio_filtro': espacio_filtro,
    })


@staff_member_required(login_url='/accounts/login/')
def reservas_lista(request):
    estado_filtro = request.GET.get('estado', 'todas')
    q = request.GET.get('q', '')
    reservas = Reserva.objects.select_related('cliente', 'espacio', 'paquete').order_by('fecha')
    if estado_filtro != 'todas':
        reservas = reservas.filter(estado=estado_filtro)
    if q:
        reservas = reservas.filter(
            Q(codigo__icontains=q) |
            Q(cliente__first_name__icontains=q) |
            Q(cliente__last_name__icontains=q) |
            Q(cliente__email__icontains=q)
        )
    filtros = [
        ('todas', 'Todas'),
        ('confirmada', 'Confirmada'),
        ('pendiente_liquidacion', 'Pendiente liquidación'),
        ('completada', 'Completada'),
    ]
    return render(request, 'operations/reservas_lista.html', {
        'reservas': reservas,
        'estado_filtro': estado_filtro,
        'q': q,
        'filtros': filtros,
    })


@staff_member_required(login_url='/accounts/login/')
def reservas_detalle(request, codigo):
    reserva = get_object_or_404(Reserva, codigo=codigo)
    actividad = reserva.actividad.select_related('usuario').order_by('-created_at')[:10]

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'registrar_pago':
            monto = request.POST.get('monto')
            if monto:
                try:
                    monto_dec = Decimal(monto.replace(',', ''))
                    PagoRegistro.objects.create(
                        reserva=reserva,
                        monto=monto_dec,
                        fecha_pago=date.today(),
                        concepto='liquidacion',
                        registrado_por=request.user,
                    )
                    reserva.anticipo_pagado += monto_dec
                    if reserva.anticipo_pagado >= reserva.total_evento:
                        reserva.estado = 'completada'
                    reserva.save()
                    ActividadReserva.objects.create(
                        reserva=reserva,
                        descripcion=f'Pago registrado: ${monto_dec:,.0f}',
                        usuario=request.user,
                    )
                except Exception:
                    pass
        elif action == 'guardar_notas':
            reserva.notas_internas = request.POST.get('notas', '')
            reserva.save()
        elif action == 'marcar_confirmada':
            reserva.estado = 'confirmada'
            reserva.save()
            ActividadReserva.objects.create(
                reserva=reserva,
                descripcion='Estado cambiado a Confirmada',
                usuario=request.user,
            )
        return redirect('operations:reservas_detalle', codigo=codigo)

    return render(request, 'operations/reservas_detalle.html', {
        'reserva': reserva,
        'actividad': actividad,
    })


@staff_member_required(login_url='/accounts/login/')
def catalogo_ops(request):
    espacios = Espacio.objects.all().order_by('orden')
    paquetes = Paquete.objects.all().prefetch_related('items')
    servicios = ServicioAdicional.objects.all().order_by('orden')
    tab = request.GET.get('tab', 'espacios')
    tabs = [('espacios', 'Espacios'), ('paquetes', 'Paquetes'), ('servicios', 'Servicios adicionales')]
    return render(request, 'operations/catalogo.html', {
        'espacios': espacios,
        'paquetes': paquetes,
        'servicios': servicios,
        'tab': tab,
        'tabs': tabs,
    })


@staff_member_required(login_url='/accounts/login/')
def reportes(request):
    anio = int(request.GET.get('anio', date.today().year))
    reservas_anio = Reserva.objects.filter(fecha__year=anio)

    ingresos_anio = reservas_anio.aggregate(t=Sum('total_evento'))['t'] or 0
    eventos_celebrados = reservas_anio.filter(estado='completada').count()
    ticket_promedio = (ingresos_anio / eventos_celebrados) if eventos_celebrados else 0

    # Ingresos por mes
    ingresos_mes = []
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    for m in range(1, 13):
        total = reservas_anio.filter(fecha__month=m).aggregate(t=Sum('total_evento'))['t'] or 0
        ingresos_mes.append({'mes': meses[m - 1], 'total': float(total)})

    # Mix por tipo
    tipo_mix = []
    for choice_val, choice_label in Reserva.TIPO_EVENTO_CHOICES:
        count = reservas_anio.filter(tipo_evento=choice_val).count()
        tipo_mix.append({'tipo': choice_label, 'count': count})

    # Top espacios
    top_espacios = []
    total_ev = reservas_anio.count() or 1
    for esp in Espacio.objects.filter(estado='publicado').order_by('orden'):
        count = reservas_anio.filter(espacio=esp).count()
        top_espacios.append({
            'espacio': esp,
            'count': count,
            'pct': round(count / total_ev * 100),
        })

    return render(request, 'operations/reportes.html', {
        'anio': anio,
        'ingresos_anio': ingresos_anio,
        'eventos_celebrados': eventos_celebrados,
        'ticket_promedio': ticket_promedio,
        'nps': 76,
        'ingresos_mes': ingresos_mes,
        'tipo_mix': tipo_mix,
        'top_espacios': top_espacios,
    })
