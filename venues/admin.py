from django.contrib import admin
from .models import Espacio, EspacioImagen, EspacioCaracteristica, Paquete, PaqueteItem, ServicioAdicional, FechaOcupada


class EspacioImagenInline(admin.TabularInline):
    model = EspacioImagen
    extra = 1


class EspacioCaracteristicaInline(admin.TabularInline):
    model = EspacioCaracteristica
    extra = 1


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'capacidad_max', 'precio_base', 'estado', 'orden']
    list_filter = ['tipo', 'estado']
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [EspacioImagenInline, EspacioCaracteristicaInline]


class PaqueteItemInline(admin.TabularInline):
    model = PaqueteItem
    extra = 1


@admin.register(Paquete)
class PaqueteAdmin(admin.ModelAdmin):
    list_display = ['get_nombre_display', 'duracion_horas', 'precio_por_persona', 'es_mas_popular', 'orden']
    inlines = [PaqueteItemInline]


@admin.register(ServicioAdicional)
class ServicioAdicionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'precio_tipo', 'orden', 'activo']
    list_filter = ['activo', 'precio_tipo']


@admin.register(FechaOcupada)
class FechaOcupadaAdmin(admin.ModelAdmin):
    list_display = ['espacio', 'fecha', 'motivo']
    list_filter = ['espacio', 'motivo']
