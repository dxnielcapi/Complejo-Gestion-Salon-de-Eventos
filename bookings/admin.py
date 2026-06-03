from django.contrib import admin
from .models import Reserva, ReservaServicio, PagoRegistro, ActividadReserva


class ReservaServicioInline(admin.TabularInline):
    model = ReservaServicio
    extra = 0


class PagoRegistroInline(admin.TabularInline):
    model = PagoRegistro
    extra = 0


class ActividadInline(admin.TabularInline):
    model = ActividadReserva
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'cliente', 'tipo_evento', 'espacio', 'fecha', 'num_invitados', 'total_evento', 'estado']
    list_filter = ['estado', 'tipo_evento', 'espacio']
    search_fields = ['codigo', 'cliente__first_name', 'cliente__last_name', 'cliente__email']
    readonly_fields = ['codigo', 'created_at', 'updated_at']
    inlines = [ReservaServicioInline, PagoRegistroInline, ActividadInline]
