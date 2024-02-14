from django.db import models
from django.utils import timezone

# Create your models here.

class Macros(models.Model):
    TarifaSocios = models.FloatField(editable=True, default=36)
    MinimoAmigos = models.FloatField(editable=True, default=20)
    diaCobro = models.IntegerField(editable=True, default=15)
    mesCobro = models.IntegerField(editable=True, default=4)
