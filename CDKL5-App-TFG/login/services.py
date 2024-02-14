import re, os
from django.db.utils import IntegrityError
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password

from login import models, constants, forms, tokens
#
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
#
from django.core.exceptions import ValidationError

class SeveralErrorMessagesException(Exception):
    def __init__(self, list):
        super().__init__()
        self.errorList = list

def signupSocio(socioform):
    if socioform.is_valid():
        personalCode = ''
        fullName = socioform.cleaned_data['nombre'].capitalize() + " " + socioform.cleaned_data['apellidos'].title()
        initialsList = re.findall(r'[A-Z]', fullName, re.DOTALL) #buscar las iniciales en el nombre completo
        for item in initialsList:
            personalCode += item
        personalCode += str(socioform.cleaned_data['fechaNac'].year) # código de socio

        socioData = models.Socios(
            CodigoSocio=personalCode,
            Nombre=socioform.cleaned_data['nombre'],
            Apellidos=socioform.cleaned_data['apellidos'],
            FechaNacimiento=socioform.cleaned_data['fechaNac'],
            #IBAN = None,
            #TitularIBAN = None,
            #SEPA = None,
        )
        
        try:
            id = models.Socios.objects.get(CodigoSocio=socioData.CodigoSocio, Nombre=socioData.Nombre, Apellidos=socioData.Apellidos, FechaNacimiento=socioData.FechaNacimiento).id
            raise ValidationError('Socio Beneficiario ya registrado con el ID = %d' %(id))
        except models.Socios.DoesNotExist:
            socioData.save()
            id = models.Socios.objects.get(CodigoSocio=socioData.CodigoSocio, Nombre=socioData.Nombre, Apellidos=socioData.Apellidos, FechaNacimiento=socioData.FechaNacimiento).id
            return {'id': id,'code': personalCode}
    #Si salta esta excepción, el único caso es el de una fecha mal introducida    
    raise ValidationError('Fecha de nacimiento no válida. Por favor, siga el formato \"DD/MM/AAAA\" o use el calendario.')

def getSocio(idSocio):
    try:
        int(idSocio)
        socio = models.Socios.objects.get(id=idSocio)
        return socio
    except models.Socios.DoesNotExist:
        raise ValidationError('El socio beneficiario con ID \"' + idSocio + '\" no existe.') # el socio no existe
    except ValueError:
        raise ValidationError('El valor \"' + idSocio + '\" no es un ID válido.')

def getNotices(user):
    if user.is_authenticated:
        userProfile = models.UserProfiles.objects.get(UserVinculado=user)
        return userProfile.Notificar
    return None
    
def validateSocioVinculation(idSocio, codSocio):
    socio = getSocio(idSocio)
    if socio.CodigoSocio != codSocio:
        raise ValidationError('El código de socio \"' + codSocio + '\" no coincide con el del socio.')
    return socio

def validateUserData(tutorform): #cambiar
    errors = []
    if tutorform.is_valid():
        if not re.match(r'^(\(?\+[0-9]{1,3}\)?)?\ ?(6|9)[0-9]{2}\ ?[0-9]{3}\ ?[0-9]{3}$', tutorform.cleaned_data['telefono']):
            errors.append('Número de teléfono no válido. El formato debe ser: NNN NNN NNN o (+NNN) NNN NNN NNN.')
        if not re.match(r'^[0-9]{5}$', tutorform.cleaned_data['codPostal']):
            errors.append('Código postal no válido. Recuerde que son cinco dígitos.')
        if tutorform.cleaned_data['password1'] != tutorform.cleaned_data['password2']:
            errors.append('Las contraseñas no coinciden. Por favor, pruebe a reescribir su contraseña.')
        if errors:
            raise SeveralErrorMessagesException(errors)
        return True
    for field in tutorform:
        if field.errors:
            for error in field.errors:
                errors.append(error)
    if errors:
        raise SeveralErrorMessagesException(errors)
    raise ValidationError('Formulario no válido.')

def completeUserForm(tutorForm, rolUsuario):
    if validateUserData(tutorForm):
        userFormData = {
            'username': tutorForm.cleaned_data['username'],
            'email': tutorForm.cleaned_data['email'],
            'first_name': tutorForm.cleaned_data['first_name'],
            'last_name': tutorForm.cleaned_data['last_name'],
            'password1': tutorForm.cleaned_data['password1'],
            'password2': tutorForm.cleaned_data['password2'],
            'user_role': rolUsuario,
        }
        userForm = forms.UserSignupForm(userFormData) # crear formulario que especifique el rol de usuario asignado automaticamente.
        if userForm.is_valid(): #deberia ser siempre valido
            try:
                user = models.Users.objects.get(username=tutorForm.cleaned_data['username'])
                raise ValidationError('Ya existe un usuario con esa dirección e-mail.')
            except models.Users.DoesNotExist: #no existe ese email registrado
                user = userForm.save(commit=False)
                user.is_active = True
                user.save()
                return (user, tutorForm.cleaned_data['password1'])
    return None

def saveUserProfile(tutorForm, idSocio, usuarioVincular): #cambio
    if validateUserData(tutorForm): #validar formato de campos y contraseña
        socioAsociado = None
        relSocioValue = None
        permisoImagenValue = None #inicialización a none en caso de que sean datos innecesarios 
        if idSocio is not None:
            socioAsociado = models.Socios.objects.get(id=idSocio)
        telefonoRegexp = re.compile(r'(6|9)[0-9]{2}\ ?[0-9]{3}\ ?[0-9]{3}')
        telefono = telefonoRegexp.search(tutorForm.cleaned_data['telefono']).group()
        permisoImagenValue = False
        if usuarioVincular.user_role == constants.RolUsuario.USUARIO:
            relSocioValue = tutorForm.cleaned_data['relSocio']
            permisoImagenValue = tutorForm.cleaned_data['permisoImg']
        userProfileData = models.UserProfiles(
                Telefono=telefono.replace(" ", ""),
                Direccion=tutorForm.cleaned_data['direccion'],
                CodigoPostal=tutorForm.cleaned_data['codPostal'],
                Localidad=tutorForm.cleaned_data['localidad'],
                Provincia=tutorForm.cleaned_data['provincia'],
                Asociado=socioAsociado,
                UserVinculado=usuarioVincular,
                Relacion=relSocioValue,
                Notificar=tutorForm.cleaned_data['notificar'],
                PermisoImagen=permisoImagenValue,
                AceptaUsoDatos=tutorForm.cleaned_data['usoDatos'],
        )
        userProfileData.save()
        return usuarioVincular.id
    raise ValidationError('Formulario no válido')

def getUserById(userId):
    try:
        int(userId)
        user = models.Users.objects.get(id=userId, is_active=True)
        return user
    except models.Users.DoesNotExist:
        raise ValidationError('El Usuario con ID \"' + str(userId) + '\" no existe.') # el usuario no existe
    except ValueError:
        raise ValidationError('El valor \"' + str(userId) + '\" no es un ID válido.')
    
def getUserByNick(username):
    try:
        user = models.Users.objects.get(username=username, is_active=True)
        return user
    except models.Users.DoesNotExist:
        raise ValidationError('El nickname \"' + str(username) + '\" no corresponde a ningún usuario.')
    
def getUserByEmail(userEmail):
    try:
        user = models.Users.objects.get(email=userEmail, is_active=True)
        return user
    except models.Users.DoesNotExist:
        raise ValidationError('El e-mail \"' + str(userEmail) + '\" no corresponde a ningún usuario.')
    
def getUserProfile(userId):
    try:
        int(userId)
        userProfile = models.UserProfiles.objects.get(UserVinculado=userId)
        return userProfile
    except models.UserProfiles.DoesNotExist:
        raise ValidationError('El Usuario con ID \"' + str(userId) + '\" no existe.') # el usuario no existe
    except ValueError:
        raise ValidationError('El valor \"' + str(userId) + '\" no es un ID válido.')
    
def getAsociado(idUser):
    user = getUserProfile(idUser)
    return user.Asociado
   
def validateBank(bankform, socio, minAmigo): #cambiar
    errors = []
    if bankform.is_valid():
        if not re.match(r'^[A-Z]{2}[0-9]{2}(\ ?[0-9]{4}){5}$', bankform.cleaned_data['iban']):
            errors.append("El Código IBAN es inválido. Debe ser un código de 24 carácteres, los dos primeros letras mayúsculas.")
        if not socio: #validar campos de tarifa para usuarios sin socio
            if bankform.cleaned_data['tarifa'] < minAmigo:
                errors.append('Cantidad de abono inválida. El abono debe ser como mínimo de ' + str(minAmigo) + ' €')
        if errors:
            raise SeveralErrorMessagesException(errors)
        return True
    for field in bankform:
        if field.errors:
            for error in field.errors:
                errors.append(error)
    if errors:
        raise SeveralErrorMessagesException(errors)
    raise ValidationError('Formulario no válido')
    
def signupBankData(bankform, userId, minAmigo):
    user = getUserById(userId)
    socioEntry = getAsociado(userId)
    if validateBank(bankform, socioEntry, minAmigo):
        if socioEntry:
            socioEntry.IBAN = bankform.cleaned_data['iban']
            socioEntry.TitularIBAN = bankform.cleaned_data['titular']
            socioEntry.SEPA = bankform.cleaned_data['sepaDoc']
            socioEntry.save()
        else:
            userEntry = getUserById(userId=userId)
            bankEntry = models.AmigoBank(
                UserVinculado = userEntry,
                IBAN = bankform.cleaned_data['iban'],
                TitularIBAN = bankform.cleaned_data['titular'],
                SEPA = bankform.cleaned_data['sepaDoc'],
                Tarifa = round(bankform.cleaned_data['tarifa'], 2) #Asegurarse de que siempre es un número float con 2 decimales máxmio
            )
            bankEntry.save()
        user.incomplete = False
        user.save() #marcar registro como completado
        return userId         
    raise ValidationError('Formulario no válido')

def hasBankInfo(socio):
    return (socio.IBAN != '') or (socio.TitularIBAN != '') or (socio.SEPA != '')

def signupHospital(hospForm, socio):
    hospEntry = models.Hospitales(
        Nombre = hospForm.cleaned_data['nombre'],
        Localidad = hospForm.cleaned_data['localidad'],
        Provincia = hospForm.cleaned_data['provincia'],
    )
    try:
        models.Hospitales.objects.get(Nombre=hospEntry.Nombre)
        raise ValidationError('Hospital ya registrado.')
    except models.Hospitales.DoesNotExist:
        hospEntry.save()
        hospital = models.Hospitales.objects.get(Nombre=hospEntry.Nombre)
        relEntry = models.HospitalizaA(
            Hospital = hospital,
            Socio = socio,
            Tvi = timezone.now().date(),
        )
        relEntry.save()
        return 'Hospital de referencia registrado correctamente.'

def signupOptData(form, userId, OptDataType):
    socio = getAsociado(userId)
    if OptDataType == 'Hospitales':
        return signupHospital(form, socio)
    raise ValidationError('Entidad a registrar no encontrada o no existe.')

def changeUserPassword(pwdForm, userEmail):
    if pwdForm.is_valid():
        if pwdForm.cleaned_data['password1'] != pwdForm.cleaned_data['password2']:
            raise ValidationError('Las contraseñas no coinciden.')
        try:
            userInstance = models.Users.objects.get(email=userEmail)
            validate_password(password=pwdForm.cleaned_data['password1'], user=userInstance)
            userInstance.set_password(pwdForm.cleaned_data['password1'])
            userInstance.save()
            return pwdForm.cleaned_data['password1']
        except models.Users.DoesNotExist:
            raise ValidationError('El usuario con e-mail \"' + userEmail + '\" no está registrado.')
    raise ValidationError('Formulario no válido.')

# ----------------------------------------------------------------------------------------
#                 UPDATE FUNCTIONS
# ----------------------------------------------------------------------------------------

def sendResetEmail(emailForm):
    if emailForm.is_valid():
        to_email = emailForm.cleaned_data['email']
        user = getUserByEmail(to_email)
        nombre = user.first_name
        apellidos = user.last_name
        current_site = 'CDKL5'
        mail_subject = 'Restauración de contraseña'
        domain = '85.31.238.158:80' #cambiar con dominio definitivo
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = tokens.passwordToken.make_token(user)
        url = f"http://{domain}/passwordReset/{uid}/{token}"
        #print('url=')
        #print(url)

        content = f"Hola {nombre} {apellidos} \n" \
                    f"Por favor da click en el enlace o copialo y pégalo en el navegador para confirmar tu cambio de contraseña en el sistema: {url} \n" \
                    f"Gracias."
        email = EmailMultiAlternatives(mail_subject, content, 'cdkl5appmail@gmail.com', [to_email])

        html_content = f"Hola <strong>{nombre} {apellidos}</strong>. <br> <br>" \
                        f"Por favor da click en el enlace para confirmar tu tu cambio de contraseña en el sistema: <a href='{url}'>{url}</a> <br> <br>" \
                        f"Gracias."
        email.attach_alternative(html_content, "text/html")

        email.send()
        return [
            'Se ha enviado un e-mail a \"' + to_email + '\".', 
            ' Para cambiar su contraseña, siga el enlace proporcionado en el correo.'
            ]
    
    raise ValidationError('Email no válido. Recuerde que un e-mail sigue el patrón \"emailNombre@dominio.extension\"')

def activate(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = models.Users.objects.get(pk=uid)
    except Exception as exn:
        return None
    if user is not None and tokens.passwordToken.check_token(user, token):
        user.is_active = True
        user.save()
        return user
    return None

def sendConfirmationEmail(userEmail):
    to_email = userEmail
    user = getUserByEmail(to_email)
    user.is_active = False
    user.save()
    nombre = user.first_name
    apellidos = user.last_name
    mail_subject = 'Confirmación del registro APP CDKL5'
    domain = '85.31.238.158:80' #Cambiar con dominio definitivo
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = tokens.passwordToken.make_token(user)
    url = f"http://{domain}/signupConfirm/{uid}/{token}"
    #print('url=')
    #print(url)

    content = f"Hola {nombre} {apellidos} \n" \
                f"Por favor da click en el enlace o copialo y pégalo en el navegador para confirmar tu registro en el sistema: {url} \n" \
                f"Gracias."
    email = EmailMultiAlternatives(mail_subject, content, 'cdkl5appmail@gmail.com', [to_email])

    html_content = f"Hola <strong>{nombre} {apellidos}</strong>. <br> <br>" \
                    f"Por favor da click en el enlace para confirmar tu registro en el sistema: <a href='{url}'>{url}</a> <br> <br>" \
                    f"Gracias."
    email.attach_alternative(html_content, "text/html")

    email.send()
    return [
        'Se ha enviado un e-mail a \"' + to_email + '\".',
        ' Para continuar el registro, siga el enlace proporcionado en el correo.',
        '',
        'En caso de no completar el registro en los siguientes tres días, ', 
        'su cuenta será eliminada junto a los datos registrados.']

def parseGlobalUpdateData(unparsedData, requestFiles, username):
    userInvolved = getUserByNick(username) # no puede fallar
    formsDict = {}
    userForm = forms.UserModForm(unparsedData, instance=userInvolved)
    formsDict['id'] = userInvolved.id
    formsDict['user'] = userForm
    if userInvolved.user_role == constants.RolUsuario.AMIGO:
        profileForm = forms.AmigoProfileForm(unparsedData)
        bankForm = forms.AmigoBankModForm(unparsedData, requestFiles)
        formsDict['profile'] = profileForm
        formsDict['bank'] = bankForm
    else:
        profileForm = forms.TutorProfileForm(unparsedData)
        socioForm = forms.SocioModForm(unparsedData)
        socioBankForm = forms.SocioBankModForm(unparsedData, requestFiles)
        formsDict['profile'] = profileForm
        formsDict['socio'] = socioForm
        formsDict['bank'] = socioBankForm
    return formsDict

def reallocateData(formsDict):
    dataList = []
    path = None
    user = getUserById(formsDict['id'])
    userForm =  formsDict['user']
    profileForm = formsDict['profile']
    dataList.append(('Datos Principales del usuario', userForm))
    dataList.append(('Datos Adicionales del Usuario', profileForm))
    if user.user_role == constants.RolUsuario.AMIGO:
        bankData = models.AmigoBank.objects.get(UserVinculado=user)
        bankForm = formsDict['bank']
        dataList.append(('Datos Bancarios', bankForm))
        path = bankData.SEPA
    else:
        socio = getAsociado(formsDict['id'])
        socioForm =  formsDict['socio']
        socioBankForm = formsDict['bank']
        dataList.append(('Socio Asociado: ' + socio.CodigoSocio, socioForm))
        dataList.append(('Datos Bancarios del Socio B.:', socioBankForm))
        path = socio.SEPA
    return (path, dataList)

def validateUserUpdates(userForm, profileForm):
    errors = []
    if profileForm.is_valid():
        if not re.match(r'^(\(?\+[0-9]{1,3}\)?)?\ ?(6|9)[0-9]{2}\ ?[0-9]{3}\ ?[0-9]{3}$', profileForm.cleaned_data['telefono']):
            errors.append('En Datos Adicionales: ' + 'Número de teléfono no válido. El formato debe ser: NNN NNN NNN o (+NNN) NNN NNN NNN.')
        if not re.match(r'^[0-9]{5}$', profileForm.cleaned_data['codPostal']):
            errors.append('En Datos Adicionales: ' + 'Código postal no válido. Recuerde que son cinco dígitos.')

        if not userForm.is_valid():
            for field in userForm:
                for error in field.errors:
                    errors.append('En datos Principales: ' +error)
        return errors
    raise ValidationError('formulario no válido')

def validateBankUpdates(bankForm, socioForm):
    errors = []
    minFloatValue = 20
    if bankForm.is_valid():
        if not re.match(r'^[A-Z]{2}[0-9]{2}(\ ?[0-9]{4}){5}$', bankForm.cleaned_data['iban']):
            errors.append('En Datos Bancarios: ' + "El Código IBAN es inválido. Debe ser un código de 24 carácteres, los dos primeros letras mayúsculas.")
        if not socioForm: #validar campos de tarifa para usuarios sin socio
            if bankForm.cleaned_data['tarifa'] < minFloatValue:
                errors.append('En Datos Bancarios: ' + 'Cantidad de abono inválida. El abono debe ser como mínimo de ' + str(minFloatValue) + ' €')
        else:
            if not socioForm.is_valid():
                for field in socioForm:
                    for error in field.errors:
                        errors.append('En Datos de Socio B.: ' + error)
        
        return errors
    raise ValidationError('Formulario no válido')

def validateUserRole(userForm, socio):
    errors = []
    if userForm.is_valid():
        role = userForm.cleaned_data['user_role']
        if socio and role == constants.RolUsuario.AMIGO:
            errors.append('Acción no recomendable: Un amigo no debería tener asociado. Cambie el rol de usuario.')
        if userForm.cleaned_data['is_staff'] and (role == constants.RolUsuario.AMIGO or role == constants.RolUsuario.USUARIO):
            errors.append('Acción no recomendable: Usuario con privilegios de administración no es parte de la asociación. \n Por favor, asigne un rol como Personal, Secretaría, Tesorería o Presidencia.')
        if role == constants.RolUsuario.USUARIO and not socio:
            errors.append('Acción no permitida: Para ser un Usuario debe tenerse asociado un socio b.')
        if role != constants.RolUsuario.AMIGO and not socio: #si hay rol del staff sin socio
            errors.append('Acción no permitida: Para pertenecer al personal de la asociación es necesario tener asociado un socio b.')
        
    return errors
    #raise ValidationError('Formulario no válido')

def updateData(formsDict, userId):
    errors = []

    userProfile = getUserProfile(userId) #obtener instancia
    user = userProfile.UserVinculado
    socio = userProfile.Asociado

    #obtener los formularios
    userForm = formsDict['user'] #is_valid llega
    profileForm  = formsDict['profile']
    errors.extend(validateUserUpdates(userForm, profileForm)) #validar. Añadir errores si hay
    #validateUserData(profileForm) no sirve por las passwords
    
    if user.user_role == constants.RolUsuario.AMIGO:
        bankForm = formsDict['bank']
        errors.extend(validateBankUpdates(bankForm, None)) #validar sin socio

    else:
        socioForm = formsDict['socio'] 
        socioBankForm = formsDict['bank']
        errors.extend(validateBankUpdates(socioBankForm, socioForm)) #validar con socio

    errors.extend(validateUserRole(userForm, socio))
    if errors:
        raise SeveralErrorMessagesException(errors)#enviar todas las excepciones
    
    #Validación completa. Iniciar la actualización

    userForm.save() #guardar cambios en user
    
    userProfile.Telefono = profileForm.cleaned_data['telefono']
    userProfile.Direccion = profileForm.cleaned_data['direccion']
    userProfile.CodigoPostal = profileForm.cleaned_data['codPostal']
    userProfile.Localidad = profileForm.cleaned_data['localidad']
    userProfile.Provincia = profileForm.cleaned_data['provincia']
    userProfile.Notificar = profileForm.cleaned_data['notificar']
    userProfile.AceptaUsoDatos = profileForm.cleaned_data['usoDatos']
    if socio:
        userProfile.Relacion = profileForm.cleaned_data['relSocio']
        userProfile.PermisoImagen = profileForm.cleaned_data['permisoImg']
    
    userProfile.save()

    if not socio:
        bank = models.AmigoBank.objects.get(UserVinculado = user)
        bank.IBAN = bankForm.cleaned_data['iban']
        bank.TitularIBAN = bankForm.cleaned_data['titular']
        bank.Tarifa = bankForm.cleaned_data['tarifa']

        if bankForm.cleaned_data['sepaDoc']: #actualizar SOLO si hay nuevo path de fichero
            if bank.SEPA:
                os.remove(bank.SEPA.path) #eliminar anterior fichero
                print('document ' + bank.SEPA.path + ' removed.')
            bank.SEPA = bankForm.cleaned_data['sepaDoc']

        bank.save()
    else:
        socio.Nombre = socioForm.cleaned_data['nombre']
        socio.Apellidos = socioForm.cleaned_data['apellidos']
        socio.FechaNacimiento = socioForm.cleaned_data['fechaNac']
        socio.IBAN = socioBankForm.cleaned_data['iban']
        socio.TitularIBAN = socioBankForm.cleaned_data['titular']
        
        if socioBankForm.cleaned_data['sepaDoc']: #actualizar SOLO si hay nuevo path de fichero
            if socio.SEPA:
                os.remove(socio.SEPA.path) #eliminar anterior fichero
                print('document ' + socio.SEPA.path + ' removed.')
            socio.SEPA = socioBankForm.cleaned_data['sepaDoc']

        socio.save()
    
    return 'Cambios Guardados exitosamente.'
    
def keepsStaff(userId):
    user = getUserById(userId)
    return user.is_staff

def updatePays(updateInfoList):
    sociosTrue = [int(infoToken.split(':')[1]) for infoToken in updateInfoList if infoToken.split(':')[0] == 'SOC'] #lista de IDs de socio con pago=True
    amigosTrue = [int(infoToken.split(':')[1]) for infoToken in updateInfoList if infoToken.split(':')[0] == 'AMG'] #lista de IDs de amigos con pago=True
    socios = models.Socios.objects.all()
    amigoBank = models.AmigoBank.objects.all()

    for socio in socios:
        socio.PagoRegistrado = (socio.id in sociosTrue) #cambiar el booleano al valor correspondiente. Si el ID de socio está en la lista de True -> True
        socio.save()                                   #Si no está presente -> False

    for bankInstance in amigoBank:
        bankInstance.PagoRegistrado = (bankInstance.UserVinculado.id in amigosTrue) #cambiar el booleano al valor correspondiente. Si el ID de usuario amigo está en la lista True -> True
        bankInstance.save()                                                        #Si no está en la lista -> False
    
    return 'Registro de pagos actualizado exitosamente.'

def addLog(user):
    logEntry = models.AccessLog(
        User = user,
        Login = user.last_login,
        #Logout = timezone.now(),
    )
    logEntry.save()

# ----------------------------------------------------------------------------------------
#                 DELETE FUNCTIONS
# ----------------------------------------------------------------------------------------

def deleteUserData(userId):
    user = models.Users.objects.get(id=userId)
    socio = getAsociado(user.id)
    if socio is None: #si es un Amigo, los datos bancarios se encuentran en otro 
        try:
            bankData = models.AmigoBank.objects.get(UserVinculado=user)
            if bankData.SEPA.path:
                os.remove(bankData.SEPA.path) #eliminar documento
        except models.AmigoBank.DoesNotExist:
            pass

    user.delete() #borrar usuario. En cascada -> UserProfile + BankData (Si era amigo)
    
    if socio is not None:
        vinculatedUsers = models.UserProfiles.objects.filter(Asociado=socio)
        if not vinculatedUsers.exists():
            #Sólo en caso de que no haya más vinculaciones al socio
            if socio.SEPA.path != "":
                os.remove(socio.SEPA.path) #eliminar documento
            socio.delete() #borrar socio (si existe) y con el los datos bancarios. En cascada -> instancias HospitalizaA, pero no los Hospitales

def deleteOrphanSocios():
    socios = models.Socios.objects.all()
    for socio in socios:
        if not models.UserProfiles.objects.filter(Asociado=socio).exists():
            if socio.SEPA != "":
                os.remove(socio.SEPA.path) #eliminar documento
            socio.delete() # eliminar socios que no tengan ningún usuario vinculado
    

# ----------------------------------------------------------------------------------------
#                 DISPLAY FUNCTIONS WITH DATA INSERTS
# ----------------------------------------------------------------------------------------

def getHospLists(socio):
    hospList = models.Hospitales.objects.all()
    vinculatedIDsList = models.HospitalizaA.objects.filter(Socio=socio, Tvf__isnull=True).values_list('Hospital', flat=True)
    vinculatedHospList = models.Hospitales.objects.filter(id__in=vinculatedIDsList).values_list('Nombre', flat=True)

    return {'all': hospList, 'vinc': vinculatedHospList}

def updateHospitalVinc(hospitalName, socio):
    hospital = models.Hospitales.objects.get(Nombre=hospitalName)
    relEntry = models.HospitalizaA(
        Hospital=hospital,
        Socio=socio,
        Tvi= timezone.now().date(),
    )
    try:
        relInstance = models.HospitalizaA.objects.get(Hospital=hospital, Socio=socio, Tvf__isnull=True) #Hospital ya vinculado, acción de desvincular
        relInstance.Tvf = timezone.now().date()
        relInstance.save()
        return 'Hospital de referencia desvinculado correctamente.'
    except models.HospitalizaA.DoesNotExist: #Hay vinculaciones previas ya finalizadas
        relInstance = models.HospitalizaA.objects.filter(Hospital=hospital, Socio=socio, Tvf__isnull=False).order_by('Tvi').last()
        if relInstance is not None and relInstance.Tvi == relEntry.Tvi:
            raise ValidationError('El hospital de nombre \"' + hospitalName + '\" fue desvinculado recientemente y se ha omitido. Por favor, inténtelo más tarde.')
        #Si no hay relaciones con el hospital previas o no hay una desvinculación con fecha equivalente al momento actual, registrar nueva entrada
        relEntry.save()
        return 'Hospital de referencia vinculado correctamente.'

def updateVinculations(previousSelection, newSelection, socio, type):  
    itemsToChange = [i for i in previousSelection + newSelection if i not in previousSelection or i not in newSelection]  
                                                #Obtener diferencias entre listas:
                                                #un email presente en previous que no está en new --> desvincular
                                                #un email presente en new que no está en previous --> vincular
                                                #un email presente en ambas listas --> ya vinculado de antes que sigue sin vincular, se puede eliminar
                                                #un email no presente en ambas listas --> no vinculado que sigue desvinculado, se puede obviar
    errors = []
    if type == 'hospitals':
        for name in itemsToChange:
            try:
                updateHospitalVinc(name, socio)
            except ValidationError as exn:
                errors.append(exn.message)
    else:
        errors.append('Tipo de dato no soportado por el sistema.')
    if errors:
        raise SeveralErrorMessagesException(errors)
    return 'Cambios Guardados exitosamente.'
