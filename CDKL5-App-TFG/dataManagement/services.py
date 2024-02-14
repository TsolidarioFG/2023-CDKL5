from datetime import datetime

from login import models
from login.services import SeveralErrorMessagesException
from login.constants import RolUsuario
from django.core.paginator import Paginator
from django.db.models import Q

from login.forms import UserModForm, TutorProfileForm, AmigoProfileForm, SocioBankModForm, AmigoBankModForm, SocioModForm

from dataManagement import models as dmodels



class DisplaySecretaryObject(object):
    def __init__(self, EditLink, Email, Nombre, Apellidos, Rol, Socio):
        self.EditLink = EditLink
        self.Email = Email
        self.Nombre = Nombre
        self.Apellidos = Apellidos
        self.Rol = Rol
        self.Socio = Socio

def getPaginatedSecretaryList(itemsPerPage, searchQuery):
    if searchQuery:
        emailMatchedUsers = models.Users.objects.filter(email__contains=searchQuery)
        nameMatchedUsers = models.Users.objects.filter(first_name__icontains=searchQuery)
        apsMatchedUsers = models.Users.objects.filter(last_name__contains=searchQuery)

        socioCodeMatchedSocios = models.Socios.objects.filter(CodigoSocio__contains=searchQuery)
        query = models.UserProfiles.objects.filter(#buscar query en diferentes campos: email/identificador, Nombre, Apellidos (Users y Socios)
            Q(Asociado__in=socioCodeMatchedSocios) |
            Q(UserVinculado__in=emailMatchedUsers) |
            Q(UserVinculado__in=nameMatchedUsers) |
            Q(UserVinculado__in=apsMatchedUsers)
            )
    else:
        query = models.UserProfiles.objects.all() #sin criterios
    toPaginate = []
    for object in query:
        if object.UserVinculado.user_role != RolUsuario.ADMINISTRADOR and object.UserVinculado.is_active and not (object.UserVinculado.incomplete): #filtrar los no activos (borrados) y el admin (invisible)
            if object.Asociado is None:
                dispObj = DisplaySecretaryObject(
                    EditLink='/manage/users/' + str(object.id),
                    Email=object.UserVinculado.email,
                    Nombre=object.UserVinculado.first_name,
                    Apellidos=object.UserVinculado.last_name,
                    Rol=object.UserVinculado.user_role,
                    Socio='',
                )
            else:
                dispObj = DisplaySecretaryObject(
                    EditLink='/manage/users/' + str(object.id),
                    Email=object.UserVinculado.email,
                    Nombre=object.UserVinculado.first_name,
                    Apellidos=object.UserVinculado.last_name,
                    Rol=object.UserVinculado.user_role,
                    Socio=object.Asociado.CodigoSocio,
                )
            toPaginate.append(dispObj)


    return Paginator(object_list=toPaginate, per_page=itemsPerPage) #Usuarios por paginacion

class DisplayTreasuryObject(object):
    def __init__(self, Titular, IBAN, IdentificadorShow, Tarifa, Pendiente, Identificador):
        self.Titular = Titular
        self.IBAN = IBAN
        self.IdentificadorShow = IdentificadorShow
        self.Tarifa = Tarifa
        self.Pendiente = Pendiente
        self.Identificador = Identificador

def getPaginatedTreasuryList(itemsPerPage, tarifaSocios, resetPays):
    socios = models.Socios.objects.all()
    bankAmigo = models.AmigoBank.objects.all() #amigos
    toPaginate = []

    for object in bankAmigo: #mostrar bancarios de amigos
        if not object.UserVinculado.incomplete and object.UserVinculado.is_active:
            vinculado = models.Users.objects.get(id=object.UserVinculado.id)
            if resetPays:
                object.PagoRegistrado = False
                object.save()
            dispObj = DisplayTreasuryObject(
                        Titular= object.TitularIBAN,
                        IBAN= object.IBAN,
                        IdentificadorShow= vinculado.email,
                        Tarifa= object.Tarifa,
                        Pendiente= object.PagoRegistrado,
                        Identificador= 'AMG' + ':' + str(vinculado.id),
                    )
            toPaginate.append(dispObj)

    for socio in socios: #mostrar bancarios de socios
        tutores = [i for i in models.UserProfiles.objects.filter(Asociado=socio) if i.UserVinculado.is_active] #tutores con is_active=True
        if tutores: #si tiene tutores activos, el socio debe mostrarse
            if resetPays:
                socio.PagoRegistrado = False
                socio.save()
            dispObj = DisplayTreasuryObject(
                    Titular= socio.TitularIBAN,
                    IBAN= socio.IBAN,
                    IdentificadorShow= socio.CodigoSocio,
                    Tarifa= tarifaSocios,
                    Pendiente= socio.PagoRegistrado,
                    Identificador= 'SOC' + ':' + str(socio.id),
                )
            toPaginate.append(dispObj)

    return Paginator(object_list=toPaginate, per_page=itemsPerPage) #Usuarios por paginacion

def getAllUserData(profileId):
    profile = models.UserProfiles.objects.get(id=profileId)
    dataList = []
    socio = profile.Asociado
    user = profile.UserVinculado
    path = None

    userNick = user.username

    userFormDict = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'user_role': user.user_role,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        
    }
    userForm = UserModForm(userFormDict)
    dataList.append(('Datos Principales del usuario', userForm))

    if user.user_role == RolUsuario.AMIGO:
        userProfDict = {
            'telefono': profile.Telefono,
            'direccion': profile.Direccion,
            'codPostal': profile.CodigoPostal,
            'localidad': profile.Localidad,
            'provincia': profile.Provincia,
            'notificar': profile.Notificar,
            'usoDatos': profile.AceptaUsoDatos,

        }
        userProfForm = AmigoProfileForm(userProfDict)
        dataList.append(('Datos Adicionales del Usuario', userProfForm))
        amigoBankData = models.AmigoBank.objects.get(UserVinculado=user)
        
        bankDict = {
            'iban': amigoBankData.IBAN,
            'titular': amigoBankData.TitularIBAN,
            'sepaDoc': amigoBankData.SEPA,
            'tarifa': amigoBankData.Tarifa,
        }

        bankForm = AmigoBankModForm(bankDict)
        dataList.append(('Datos Bancarios', bankForm))

        path = amigoBankData.SEPA
    else:
        userProfDict = {
            'telefono': profile.Telefono,
            'direccion': profile.Direccion,
            'codPostal': profile.CodigoPostal,
            'localidad': profile.Localidad,
            'provincia': profile.Provincia,
            'relSocio': profile.Relacion,
            'notificar': profile.Notificar,
            'permisoImg': profile.PermisoImagen,
            'usoDatos': profile.AceptaUsoDatos,

        }
        
        socioDict = {
            'id': socio.id,
            'nombre': socio.Nombre,
            'apellidos': socio.Apellidos,
            'fechaNac': socio.FechaNacimiento,
        }

        socioBankDict = {
            'iban': socio.IBAN,
            'titular': socio.TitularIBAN,
            'sepaDoc': socio.SEPA,
        }
        
        socioBankForm = SocioBankModForm(socioBankDict)
        socioForm = SocioModForm(socioDict)
        userProfForm = TutorProfileForm(userProfDict)
        dataList.append(('Datos Adicionales del Usuario', userProfForm))
        dataList.append(('Socio Asociado: ' + socio.CodigoSocio, socioForm))
        dataList.append(('Datos Bancarios del Socio B.:', socioBankForm))
        path = socio.SEPA

    return (path, userNick, dataList)

def getGeneralVars():
    instance = dmodels.Macros.objects.all().last() #obtener instancia Única (la mas reciente registrada)
    dateStr = str(instance.diaCobro) + '-' + str(instance.mesCobro) + '-' + str(datetime.now().year)
    date = datetime.strptime(dateStr, '%d-%m-%Y') 
    return {'minAmigo': instance.MinimoAmigos, 'tarSocio': instance.TarifaSocios, 'payDate': date}

def validatePayForm(payForm):
    errors = []
    if payForm.is_valid():
        if payForm.cleaned_data['minAmigo'] <= 0:
            errors.append('el mínimo a pagar de los amigos debe ser mayor a cero.')
        if payForm.cleaned_data['tarSocio'] <= 0:
            errors.append('La Tarifa de los usuarios con socio b. debe ser mayor a cero.')
    else:
        errors.append('Fecha de cobro inválida. Por favor, seleccione una fecha correcta del calendario.')
    if errors:
        raise SeveralErrorMessagesException(errors)
    return True

def updateGeneralVars(varsForm):
    if validatePayForm(varsForm):
        instance = dmodels.Macros.objects.all().last() #obtener instancia Única (la mas reciente registrada)
        instance.MinimoAmigos = round(varsForm.cleaned_data['minAmigo'], 2)
        instance.TarifaSocios = round(varsForm.cleaned_data['tarSocio'], 2) #Asegurarse de que siempre son números float con 2 decimales máxmio
        instance.diaCobro = varsForm.cleaned_data['payDate'].day
        instance.mesCobro = varsForm.cleaned_data['payDate'].month
        instance.save()
        return 'Parámetros actualizados exitosamente.'
