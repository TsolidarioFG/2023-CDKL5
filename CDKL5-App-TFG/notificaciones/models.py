from django.db import models
from login.models import Users
from django.utils import timezone
from notificaciones import constants

# Create your models here.

class Notice(models.Model):
    Creador = models.ForeignKey(to=Users, on_delete=models.CASCADE, default=None, null=False)
    Destino = models.CharField(max_length=5, choices=constants.NoticeScope.choices, default=constants.NoticeScope.TODOS, null=True)
    Titulo = models.CharField(max_length=30)
    Texto = models.CharField(max_length=400, null=False)
    Adjunto = models.FileField(upload_to='attached/%Y/%m/%d')
    FechaCreacion = models.DateTimeField(default=timezone.now, editable=False)

class Vistos(models.Model):
    Notice = models.ForeignKey(to=Notice, on_delete=models.CASCADE, default=None, null=False)
    User = models.ForeignKey(to=Users, on_delete=models.CASCADE, default=None, null=False)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Notice', 'User'], name='Complex Primary Key simulation for Vistos.')
        ]