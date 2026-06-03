from django.db import models
from django.utils.text import slugify


class Espacio(models.Model):
    TIPO_CHOICES = [
        ('interior_climatizado', 'Interior · Climatizado'),
        ('exterior_tropical', 'Exterior · Tropical'),
        ('exterior_cubierto', 'Exterior Cubierto · Vista al Mar'),
        ('interior_versatil', 'Interior · Versátil'),
    ]
    ESTADO_CHOICES = [
        ('publicado', 'Publicado'),
        ('borrador', 'Borrador'),
    ]

    nombre = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    capacidad_max = models.PositiveIntegerField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    precio_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='publicado')
    imagen_principal = models.ImageField(upload_to='espacios/', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, help_text='Etiquetas separadas por ·')
    color_card = models.CharField(max_length=20, default='#C9A96E', help_text='Color hex de la tarjeta')
    eventos_por_dia = models.PositiveSmallIntegerField(default=1)
    ubicacion = models.CharField(max_length=100, default='Complejo Riviera Maya')
    orden = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_tipo_label(self):
        return self.get_tipo_display()

    def get_tipo_grupo(self):
        """Devuelve 'interior' o 'exterior' para los filtros del catálogo."""
        if self.tipo in ('interior_climatizado', 'interior_versatil'):
            return 'interior'
        return 'exterior'

    def tiene_vista_al_mar(self):
        return self.tipo == 'exterior_cubierto'


class EspacioImagen(models.Model):
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='espacios/galeria/')
    caption = models.CharField(max_length=100, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Imagen de Espacio'
        verbose_name_plural = 'Imágenes de Espacio'
        ordering = ['orden']

    def __str__(self):
        return f'{self.espacio.nombre} — imagen {self.orden}'


class EspacioCaracteristica(models.Model):
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name='caracteristicas')
    descripcion = models.CharField(max_length=150)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Característica de Espacio'
        verbose_name_plural = 'Características de Espacio'
        ordering = ['orden']

    def __str__(self):
        return f'{self.espacio.nombre}: {self.descripcion}'


class Paquete(models.Model):
    NOMBRE_CHOICES = [
        ('basico', 'Básico'),
        ('premium', 'Premium'),
        ('lujo', 'Lujo'),
    ]

    nombre = models.CharField(max_length=20, choices=NOMBRE_CHOICES, unique=True)
    descripcion_corta = models.CharField(max_length=150)
    duracion_horas = models.PositiveSmallIntegerField()
    precio_por_persona = models.DecimalField(max_digits=10, decimal_places=2)
    es_mas_popular = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Paquete'
        verbose_name_plural = 'Paquetes'
        ordering = ['orden']

    def __str__(self):
        return self.get_nombre_display()


class PaqueteItem(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE, related_name='items')
    descripcion = models.CharField(max_length=150)
    incluido = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Item de Paquete'
        verbose_name_plural = 'Items de Paquete'
        ordering = ['orden']

    def __str__(self):
        estado = '✓' if self.incluido else '✗'
        return f'{estado} {self.paquete.get_nombre_display()}: {self.descripcion}'


class ServicioAdicional(models.Model):
    PRECIO_TIPO_CHOICES = [
        ('fijo', 'Precio fijo'),
        ('por_persona', 'Por persona'),
    ]

    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_tipo = models.CharField(max_length=15, choices=PRECIO_TIPO_CHOICES, default='fijo')
    icono_nombre = models.CharField(max_length=50, blank=True, default='sparkles')
    descripcion = models.CharField(max_length=200, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Servicio Adicional'
        verbose_name_plural = 'Servicios Adicionales'
        ordering = ['orden']

    def __str__(self):
        return self.nombre

    def precio_display(self):
        if self.precio_tipo == 'por_persona':
            return f'${self.precio:,.0f}/persona'
        return f'${self.precio:,.0f}'


class FechaOcupada(models.Model):
    MOTIVO_CHOICES = [
        ('reserva', 'Reserva'),
        ('bloqueo', 'Bloqueo administrativo'),
    ]

    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name='fechas_ocupadas')
    fecha = models.DateField()
    motivo = models.CharField(max_length=10, choices=MOTIVO_CHOICES, default='reserva')
    nota = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Fecha Ocupada'
        verbose_name_plural = 'Fechas Ocupadas'
        unique_together = ('espacio', 'fecha')

    def __str__(self):
        return f'{self.espacio.nombre} — {self.fecha}'
