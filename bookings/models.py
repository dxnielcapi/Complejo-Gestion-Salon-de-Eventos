import random
import string
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from venues.models import Espacio, Paquete, ServicioAdicional


def generar_codigo():
    year = date.today().year
    sufijo = ''.join(random.choices(string.digits, k=4))
    return f'RM-{year}-{sufijo}'


class Reserva(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('boda', 'Boda'),
        ('xv_anos', 'XV años'),
        ('bautizo', 'Bautizo'),
        ('aniversario', 'Aniversario'),
        ('empresarial', 'Empresarial'),
        ('cumpleanos', 'Cumpleaños'),
    ]
    ESTADO_CHOICES = [
        ('confirmada', 'Confirmada'),
        ('pendiente_liquidacion', 'Pendiente liquidación'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    codigo = models.CharField(max_length=20, unique=True, default=generar_codigo)
    cliente = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reservas')
    espacio = models.ForeignKey(Espacio, on_delete=models.PROTECT, related_name='reservas')
    paquete = models.ForeignKey(Paquete, on_delete=models.PROTECT, related_name='reservas')
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    num_invitados = models.PositiveIntegerField()
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='confirmada')
    total_evento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    anticipo_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notas_internas = models.TextField(blank=True)
    coordinador = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='eventos_coordinados'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.codigo} — {self.cliente.get_full_name()} ({self.get_tipo_evento_display()})'

    @property
    def saldo_pendiente(self):
        return self.total_evento - self.anticipo_pagado

    def calcular_total(self):
        base = self.espacio.precio_base
        paquete_total = self.paquete.precio_por_persona * self.num_invitados
        extras_total = sum(
            rs.servicio.precio * rs.cantidad
            for rs in self.servicios.all()
            if rs.servicio.precio_tipo == 'fijo'
        ) + sum(
            rs.servicio.precio * self.num_invitados * rs.cantidad
            for rs in self.servicios.all()
            if rs.servicio.precio_tipo == 'por_persona'
        )
        return base + paquete_total + extras_total

    def get_estado_css(self):
        css = {
            'confirmada': 'bg-green-100 text-green-700',
            'pendiente_liquidacion': 'bg-yellow-100 text-yellow-700',
            'completada': 'bg-blue-100 text-blue-700',
            'cancelada': 'bg-red-100 text-red-700',
        }
        return css.get(self.estado, '')


class ReservaServicio(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='servicios')
    servicio = models.ForeignKey(ServicioAdicional, on_delete=models.PROTECT)
    cantidad = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Servicio de Reserva'
        verbose_name_plural = 'Servicios de Reserva'
        unique_together = ('reserva', 'servicio')

    def __str__(self):
        return f'{self.reserva.codigo} — {self.servicio.nombre}'

    def subtotal(self):
        if self.servicio.precio_tipo == 'por_persona':
            return self.servicio.precio * self.reserva.num_invitados * self.cantidad
        return self.servicio.precio * self.cantidad


class PagoRegistro(models.Model):
    CONCEPTO_CHOICES = [
        ('anticipo', 'Anticipo 25%'),
        ('liquidacion', 'Liquidación'),
        ('extra', 'Cargo extra'),
    ]

    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField()
    concepto = models.CharField(max_length=15, choices=CONCEPTO_CHOICES)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f'{self.reserva.codigo} — ${self.monto:,.0f} ({self.get_concepto_display()})'


class ActividadReserva(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='actividad')
    descripcion = models.CharField(max_length=300)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reserva.codigo}: {self.descripcion}'
