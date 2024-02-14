from django import forms
from login import models
from login import constants

from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class SocioForm(forms.Form):
    #Formulario con campos
    nombre = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': 'Nombre*'}), help_text="Por favor, acuérdese de colocar la inicial en mayúscula.")
    apellidos = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Apellidos*'}), help_text="Por favor, acuérdese de colocar las iniciales en mayúscula.")
    #codigoMutacion = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'Código de Mutación'}))
    fechaNac = forms.DateField(required=True, widget=forms.DateInput(attrs={'placeholder': 'Fecha de Nacimiento*', 'id': 'datepicker', }, format='%d/%m/%Y'))

class HospitalForm(forms.Form):
    nombre = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Nombre del Hospital'}))
    localidad = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Localidad del Hospital'}))
    provincia = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Provincia del Hospital'}))

#----------------------------------------------------------------------------
class UserSignupForm(UserCreationForm): #formulario para registrar usuario

    class Meta:
        model = models.Users
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'user_role')
        

class UserRegistrationForm(UserCreationForm): #formulario para pedir datos al usuario
    username = forms.CharField(max_length=20, required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'Nickname*'}))
    email = forms.EmailField(max_length=200, required=True, label='', widget=forms.EmailInput(attrs={'placeholder': 'e-mail de usuario*'}))
    first_name = forms.CharField(max_length=100, required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'Nombre*'}))
    last_name = forms.CharField(max_length=100, required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'Apellidos*'}))
    password1 = forms.CharField(max_length=200, required=True, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña*'}))
    password2 = forms.CharField(max_length=200, required=True, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Confirme Contraseña*'}))

    class Meta:
        model = models.Users
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class TutorForm(UserRegistrationForm): #formulario de datos de tutor de socio (usuario + profile)
    telefono = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Teléfono*'}), label='')
    direccion = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': 'Dirección*'}), label='')
    codPostal = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': 'Código Postal*'}), label='')
    localidad = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Localidad*'}), label='')
    provincia = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Provincia'}), label='')
    relSocio = forms.ChoiceField(choices=constants.Relaciones.choices, label='Relación con el socio b.:*')
    notificar = forms.BooleanField(required=False, label='Deseo recibir notificaciones de parte de la Asociación:', widget=forms.CheckboxInput())
    permisoImg = forms.BooleanField(required=False, label='Autorizo el uso de imágenes del socio beneficiario en la Asociación:', widget=forms.CheckboxInput())
    usoDatos = forms.BooleanField(required=True, label='He leído y acepto ', widget=forms.CheckboxInput())

class AmigoForm(UserRegistrationForm): #formulario de datos de amigo (usuario + profile)
    telefono = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Teléfono*'}), label='')
    direccion = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': 'Dirección*'}), label='')
    codPostal = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'placeholder': 'Código Postal*'}), label='')
    localidad = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Localidad*'}), label='')
    provincia = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Provincia'}), label='')
    notificar = forms.BooleanField(required=False, label='Deseo recibir notificaciones de parte de la Asociación:', widget=forms.CheckboxInput())
    usoDatos = forms.BooleanField(required=True, label='He leído y acepto ', widget=forms.CheckboxInput())

class AmigoBankForm(forms.Form):
    iban = forms.CharField(max_length=34, required=True, widget=forms.TextInput(attrs={'placeholder': 'IBAN*'}), label='')
    titular = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': 'Titular de la cuenta*'}), label='')
    sepaDoc = forms.FileField(required=True, label='Inserte Documento SEPA*:')
    tarifa = forms.FloatField(required=True, widget=forms.NumberInput(attrs={'placeholder': 'Cantidad a abonar (€)*'}), initial=20.00, label='')

class SocioBankForm(forms.Form):
    iban = forms.CharField(max_length=34, required=True, widget=forms.TextInput(attrs={'placeholder': 'IBAN*'}), label='')
    titular = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'placeholder': 'Titular de la cuenta*'}), label='')
    sepaDoc = forms.FileField(required=True, label='Inserte Documento SEPA*:')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=200, required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'Nickname del usuario*'}))
    #email = forms.CharField(max_length=200, required=True, label='', widget=forms.TextInput(attrs={'placeholder': 'e-mail del usuario*'}))
    password = forms.CharField(max_length=200, required=True, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña*'}))

class askEmailForm(forms.Form):
    email = forms.EmailField(max_length=200, required=True, label='', widget=forms.EmailInput(attrs={'placeholder': 'e-mail de usuario*'}))

class PasswordForm(forms.Form):
    password1 = forms.CharField(max_length=200, required=True, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Nueva Contraseña*'}))
    password2 = forms.CharField(max_length=200, required=True, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Nueva Contraseña*'}))

#---------------------MODIFICATION FORMS-------------------------

class UserModForm(UserChangeForm):
    password = None
    username = forms.CharField(max_length=20, required=True, label='Nickname*: ', widget=forms.TextInput(attrs={}))
    email = forms.EmailField(max_length=200, required=True, label='e-mail de usuario*: ', widget=forms.EmailInput(attrs={}))
    first_name = forms.CharField(max_length=100, required=True, label='Nombre*: ', widget=forms.TextInput(attrs={}))
    last_name = forms.CharField(max_length=100, required=True, label='Apellidos*: ', widget=forms.TextInput(attrs={}))
    is_staff = forms.BooleanField(required=False, label='Permitir al usuario acceder a los datos de la asociación: ', widget=forms.CheckboxInput())
    is_active = forms.BooleanField(required=False, label='Usuario dado de alta: ', widget=forms.CheckboxInput(attrs={'id': "erase"}))
    user_role = forms.ChoiceField( label='Rol del Usuario: ')
    class Meta:
        model = models.Users
        fields = ('username', 'email', 'first_name', 'last_name', 'user_role', 'is_staff', 'is_active')

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        banned_choices = [constants.RolUsuario.ADMINISTRADOR, ] #opciones que deben permanecer ocultas
        self.fields['user_role'].choices = [(v, k) for v, k in constants.RolUsuario.choices
                                                if v not in banned_choices]

class TutorProfileForm(forms.Form):
    telefono = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={}), label='Teléfono*: ')
    direccion = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={}), label='Dirección*: ')
    codPostal = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={}), label='Código Postal*: ')
    localidad = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={}), label='Localidad*: ')
    provincia = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={}), label='Provincia: ')
    relSocio = forms.ChoiceField(choices=constants.Relaciones.choices, label='Relación con el socio b.:*')
    notificar = forms.BooleanField(required=False, label='Desea recibir notificaciones de parte de la Asociación:', widget=forms.CheckboxInput())
    permisoImg = forms.BooleanField(required=False, label='Autoriza el uso de imágenes del socio beneficiario en la Asociación:', widget=forms.CheckboxInput())
    usoDatos = forms.BooleanField(required=False, label='Autoriza el uso de sus datos en la asociación:*', widget=forms.CheckboxInput())

class SocioModForm(forms.Form):
    id = forms.CharField(required=True, widget=forms.TextInput(attrs={'readonly': True}), label='ID Numérico:')
    nombre = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={}), label= 'Nombre*')
    apellidos = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={}), label='Apellidos*')
    #codigoMutacion = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={}), label= 'Código de Mutación')
    fechaNac = forms.DateField(required=True, widget=forms.DateInput(attrs={'id': 'datepicker', }, format='%d/%m/%Y'), label='Fecha de Nacimiento*')

class SocioBankModForm(forms.Form):
    iban = forms.CharField(max_length=34, required=True, widget=forms.TextInput(attrs={}), label='IBAN*: ')
    titular = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={}), label='Titular de la cuenta*: ')
    sepaDoc = forms.FileField(required=False, label='Documento SEPA:')

class AmigoProfileForm(forms.Form):
    telefono = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={}), label='Teléfono*: ')
    direccion = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={}), label='Dirección*: ')
    codPostal = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={}), label='Código Postal*: ')
    localidad = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={}), label='Localidad*: ')
    provincia = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={}), label='Provincia: ')
    notificar = forms.BooleanField(required=False, label='Desea recibir notificaciones de parte de la Asociación:', widget=forms.CheckboxInput())
    usoDatos = forms.BooleanField(required=False, label='Autoriza el uso de sus datos en la asociación:*', widget=forms.CheckboxInput())

class AmigoBankModForm(forms.Form):
    iban = forms.CharField(max_length=34, required=True, widget=forms.TextInput(attrs={}), label='IBAN*: ')
    titular = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={}), label='Titular de la cuenta*: ')
    tarifa = forms.FloatField(required=True, widget=forms.NumberInput(attrs={}), label='Abono Anual (€)*')
    sepaDoc = forms.FileField(required=False, label='Documento SEPA:')
