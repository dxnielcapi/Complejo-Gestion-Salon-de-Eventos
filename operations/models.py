from django.db import models
from django.contrib.auth.models import User


class TareaPendiente(models.Model):
    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    descripcion = models.CharField(max_length=200)
    completada = models.BooleanField(default=False)
    asignado_a = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tareas'
    )
    prioridad = models.CharField(max_length=5, choices=PRIORIDAD_CHOICES, default='media')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tarea Pendiente'
        verbose_name_plural = 'Tareas Pendientes'
        ordering = ['-created_at']

    def __str__(self):
        return self.descripcion

    def get_color(self):
        colors = {'alta': '#E07E5D', 'media': '#C9A96E', 'baja': '#2D7A7A'}
        return colors.get(self.prioridad, '#888')
