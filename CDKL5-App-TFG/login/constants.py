from django.db.models import TextChoices

class RolUsuario(TextChoices):  #Rol del usuario. Valores posibles [Usuario, Amigo, Secretaria, Presidencia, Tesoreria, Personal]
    USUARIO = 'USR'
    AMIGO = 'AMG'
    SECRETARIA = 'SEC'
    TESORERIA = 'TES'
    PERSONAL = 'PNL'
    PRESIDENCIA = 'PRS'
    ADMINISTRADOR = 'ADM'

class Relaciones(TextChoices):
    PATERNAL = 'PAT'
    HERMANDAD = 'HRM'
    FAMILIAR = 'FML'
    OTRO = 'OTR'
