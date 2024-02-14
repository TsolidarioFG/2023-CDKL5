from django.db import models
from login.models import Users
from django.utils import timezone

# Create your models here.

class Post(models.Model):
    Creador = models.ForeignKey(to=Users, on_delete=models.CASCADE, default=None, null=False)
    Titulo = models.CharField(max_length=43) # 30 chars del título + 13 chars de estándar de respuestas: "Respuesta a: "
    Texto = models.CharField(max_length=400, null=False)
    RespuestaDe = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True) #probar
    FechaCreacion = models.DateTimeField(default=timezone.now, editable=False)
