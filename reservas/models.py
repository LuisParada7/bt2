from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TrainingType(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre")
    description = models.CharField(max_length=50, verbose_name="Descripción")
    image = models.ImageField(upload_to='training_type_images/', null=True, blank=True, verbose_name="Imagen")

    class Meta:
        verbose_name = "Tipo de entrenamiento"
        verbose_name_plural = "Tipos de entrenamiento"
        ordering = ['name']

    def __str__(self):
        return self.name

class TrainingReservation(models.Model):
    date = models.DateField(verbose_name="Fecha", default=timezone.now)
    time = models.TimeField(verbose_name="Hora del entrenamiento")
    location = models.CharField(max_length=50, verbose_name="Dirección lugar de entrenamiento")
    training_type = models.ForeignKey(TrainingType, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=20, verbose_name="Celular del cliente")
    notes = models.CharField(max_length=250, verbose_name="Comentarios adicionales", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", default=None)
    google_event_id = models.CharField(max_length=255, null=True, blank=True)
    completed = models.BooleanField(default=False, verbose_name="Completado")

    class Meta:
        verbose_name = "Reserva de entrenamiento"
        verbose_name_plural = "Reservas de entrenamiento"
        ordering = ['date']

    def __str__(self):
        return f'Cita para {self.user.username} el {self.date} a las {self.time.strftime("%H:%M")}'