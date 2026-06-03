from django.contrib import admin
from .models import TareaPendiente


@admin.register(TareaPendiente)
class TareaPendienteAdmin(admin.ModelAdmin):
    list_display = ['descripcion', 'prioridad', 'completada', 'asignado_a', 'created_at']
    list_filter = ['completada', 'prioridad']
