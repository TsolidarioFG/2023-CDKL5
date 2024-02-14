from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from login.managers import UserManager
from login import constants

# Create your models here.

class Socios(models.Model):
    CodigoSocio = models.CharField(max_length=10)
    Nombre = models.CharField(max_length=15)
    Apellidos = models.CharField(max_length=50)
    #CodigoMutacion = models.CharField(max_length=50, default=None, null=True)
    FechaNacimiento = models.DateField(editable=True)
    IBAN = models.CharField(max_length=34)
    TitularIBAN = models.CharField(max_length=15)  
    SEPA = models.FileField(upload_to='sepa/%Y/%m/%d')
    PagoRegistrado = models.BooleanField(default=False)

class Users(AbstractUser): # Instancia Usuario personalizada de un User en Django
    username = models.CharField('Nickname*', max_length=20, unique=True)
    email = models.EmailField('Dirección e-mail*', unique=True)
    first_name = models.CharField('Nombre*', max_length=100)
    last_name = models.CharField('Apellidos*', max_length=100)
    user_role = models.CharField('Rol De Usuario', max_length=3, choices=constants.RolUsuario.choices, default=constants.RolUsuario.USUARIO)    #Rol del usuario. Valores posibles [Usuario, Amigo, Secretaria, Presidencia, Tesoreria, Personal]
    incomplete = models.BooleanField(default=True)

    @property
    def is_obsolete(self):
        return self.incomplete and ((timezone.now() - self.date_joined).days >= 3) #un usuario es obsoleto cuando está incompleto y pasaron 3 días


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

class UserProfiles(models.Model): # Más información de un usuario Django.
    Telefono = models.IntegerField()                                                                    #Telefono (Max. 9 dígitos)
    Direccion = models.CharField(max_length=200)
    CodigoPostal = models.IntegerField()                                                                #Codigo postal (Max. 5 dígitos)
    Localidad = models.CharField(max_length=100)                                                        #Localidad/ciudad de residencia del usuario
    Provincia = models.CharField(max_length=100)                                                        #Provincia de residencia del usuario
    Asociado = models.ForeignKey(to=Socios, on_delete=models.PROTECT, default=None, null=True)          #ID de socio. Foránea de tabla Socios
    UserVinculado = models.ForeignKey(to=Users, on_delete=models.CASCADE, default=None, null=False)
    Relacion = models.CharField(max_length=3, choices=constants.Relaciones.choices, default=constants.Relaciones.PATERNAL, null=True)
    Notificar = models.BooleanField(default=True)                                                       #Booleano de permiso para el envío de notificaciones (por defecto si)
    PermisoImagen = models.BooleanField(default=False)                                                  #Booleano de permiso para el uso de imágenes (por defecto no)
    AceptaUsoDatos = models.BooleanField(default=False)

class Hospitales(models.Model):
    Nombre = models.CharField(max_length=30)
    Localidad = models.CharField(max_length=100)
    Provincia = models.CharField(max_length=100)  

class HospitalizaA(models.Model):
    Hospital = models.ForeignKey(to=Hospitales, on_delete=models.PROTECT)
    Socio = models.ForeignKey(to=Socios, on_delete=models.CASCADE)
    Tvi = models.DateField(default=timezone.now, editable=True)
    Tvf = models.DateField(editable=True, default=None, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Hospital', 'Socio', 'Tvi'], name='Complex Primary Key simulation for HospitalizaA.')
        ]

class AmigoBank(models.Model):
    UserVinculado = models.ForeignKey(to=Users, on_delete=models.CASCADE, default=None, null=False)
    IBAN = models.CharField(max_length=34)
    TitularIBAN = models.CharField(max_length=15)  
    SEPA = models.FileField(upload_to='sepa/%Y/%m/%d')
    Tarifa = models.FloatField(editable=True, null=True)
    PagoRegistrado = models.BooleanField(default=False)

class AccessLog(models.Model):
    User = models.ForeignKey(to=Users, on_delete=models.CASCADE, default=None, null=False)
    Login = models.DateTimeField(default=timezone.now, editable=False)
    Logout = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['User', 'Login', 'Logout'], name='Complex Primary Key simulation for AccessLog.')
        ]
