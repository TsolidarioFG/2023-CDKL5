from datetime import datetime
from django.utils import timezone

import re, os
from django.test import TransactionTestCase
from login.models import Socios, Users, UserProfiles, Hospitales, HospitalizaA, AccessLog
from login.constants import RolUsuario, Relaciones
from login.forms import SocioForm, TutorForm, AmigoForm, AmigoBankForm, SocioBankForm, HospitalForm, PasswordForm
from login import services

from django.core.files.uploadedfile import SimpleUploadedFile

from django.core.exceptions import ValidationError

class testServices(TransactionTestCase):
    reset_sequences = True # evitar confilctos de ids autogenerados entre test cases

    minAmigo = 20

    socioCorrecto = Socios(
        Nombre='socioPrueba',
        Apellidos='Aps socioPrueba',
        FechaNacimiento=datetime.strptime('19/09/22', '%d/%m/%y'),
        IBAN = '',
        TitularIBAN = '',
        SEPA = '',
    )

    socioNombreVacio = Socios(
        Apellidos='Aps NoName',
        FechaNacimiento=datetime.strptime('19/09/22', '%d/%m/%y'),
        IBAN = '',
        TitularIBAN = '',
        SEPA = '',
    )

    tutorCorrecto = Users(
        username= 'tutorCorrectonick',
        email='emailtutor@email.com',
        first_name='TutorPrueba',
        last_name='Apellidos tutorPrueba',
        user_role=RolUsuario.USUARIO, 
    )

    tutorCorrectoProfile = UserProfiles(
        Telefono = '(+34) 687 446 235',
        Direccion = 'alguna direccion de prueba',
        CodigoPostal='15340',
        Localidad = 'A Coruña',
        Provincia = 'A Coruña',
        Asociado = socioCorrecto,
        UserVinculado = tutorCorrecto,
        Relacion = Relaciones.PATERNAL,
        Notificar = True,
        PermisoImagen = True,
        AceptaUsoDatos = True,
    )

    amigoCorrecto = Users(
        username= 'amigoCorrectonick',
        email='emailamigo@email.com',
        first_name='AmigoPrueba',
        last_name='Apellidos amigoPrueba',
        user_role=RolUsuario.AMIGO, 
    )

    amigoCorrectoProfile = UserProfiles(
        Telefono = '(+112) 987 653 487',
        Direccion = 'alguna direccion de prueba',
        CodigoPostal='15221',
        Localidad = 'A Coruña',
        Provincia = 'A Coruña',
        Asociado = None,
        UserVinculado = amigoCorrecto,
        Relacion = None,
        Notificar = True,
        PermisoImagen = None,
        AceptaUsoDatos = True,
    )

    def generateSocioForm(self, socio):
        socioformData = {
            'nombre': socio.Nombre,
            'apellidos': socio.Apellidos,
            'fechaNac': socio.FechaNacimiento
        }
        return SocioForm(socioformData)
    
    def generateUserForm(self, userProfile, invalidPwd, tlf='(+34) 687 446 235', cp='15340', isAmigo=False, Notificar=True, permImg=True): # valores válidos por defecto
        user = userProfile.UserVinculado
        password = 'Homepage5'
        if invalidPwd:
            password = '12345678'

        if isAmigo:
            userFormData = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password1': password,
                'password2': password,
                'user_role': RolUsuario.AMIGO,
                'telefono': tlf,
                'direccion': userProfile.Direccion,
                'codPostal': cp,
                'localidad': userProfile.Localidad,
                'provincia': userProfile.Provincia,
                'notificar': Notificar,
                'usoDatos': True,
            }
            return AmigoForm(userFormData)
        else:
            userFormData = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password1': password,
                'password2': password,
                'user_role': RolUsuario.USUARIO,
                'telefono': tlf,
                'direccion': userProfile.Direccion,
                'codPostal': cp,
                'localidad': userProfile.Localidad,
                'provincia': userProfile.Provincia,
                'relSocio': userProfile.Relacion,
                'notificar': Notificar,
                'permisoImg': permImg,
                'usoDatos': True,
            }
            return TutorForm(userFormData)
    
    def generateFileChunks(self, filename):
        f = open(filename, 'rb')
        chunks = []
        while True:
            chunk = f.read(10)
            if not chunk: break
            chunks.append(chunk)
        f.close()
        return chunks
        
    def generateBankForm(self, filename, iban='ES7100302053091234567895', titular='titularName', isAmigo=False, tarifa=20.20):
        f = self.generateFileChunks(filename)
        if isAmigo:
            formData = {
                'iban': iban,
                'titular': titular,
                'sepaDoc': f,
                'tarifa': tarifa,
            }
            with open(filename, 'rb') as file:
                form = AmigoBankForm(formData, files={'sepaDoc': SimpleUploadedFile('sepaDoc', file.read())})
                file.close()
            return form
        else:
            formData = {
                'iban': iban,
                'titular': titular,
                'sepaDoc': f,    
            }
            
            with open(filename, 'rb') as file:
                form = SocioBankForm(formData, files={'sepaDoc': SimpleUploadedFile('sepaDoc', file.read())})
                file.close()
            return form
    
    def getSocioCode(self, socioform):
        personalCode = ''
        if socioform.is_valid():
            fullName = socioform.cleaned_data['nombre'].capitalize() + " " + socioform.cleaned_data['apellidos'].title()
            initialsList = re.findall(r'[A-Z]', fullName, re.DOTALL) #buscar las iniciales en el nombre completo
            for item in initialsList:
                personalCode += item
            personalCode += str(socioform.cleaned_data['fechaNac'].year) # código de socio
        return personalCode

#---------------------------------------------------------------------------------------------------------------------------------------------------
#                                                           T E S T S
#---------------------------------------------------------------------------------------------------------------------------------------------------
    def testSignupSocio(self):
        form = self.generateSocioForm(self.socioCorrecto) # Registro válido
        socioDict = services.signupSocio(form)
        self.assertEquals(1, socioDict['id'])
        self.assertEquals(self.getSocioCode(form), socioDict['code'])

        with self.assertRaises(ValidationError):
            services.signupSocio(form) # probar que no se puede registrar otra vez

    def testSignupSocioNoName(self):
        form = self.generateSocioForm(self.socioNombreVacio) # registro sin campo obligatorio
        with self.assertRaises(ValidationError):
            services.signupSocio(form) # error de campo obligatorio no llenado
#---------------------------------------------------------------------------------------------------------------------------------------------------
    def testGetSocio(self):
        form = self.generateSocioForm(self.socioCorrecto) # Registro válido
        socioDict = services.signupSocio(form)
        self.assertEquals(1, socioDict['id'])
        self.assertEquals(self.getSocioCode(form), socioDict['code'])

        socio = services.getSocio(idSocio=1)
        self.assertEquals(socioDict['id'], socio.id)
        self.assertEquals(self.socioCorrecto.Nombre, socio.Nombre)
        self.assertEquals(self.socioCorrecto.Apellidos, socio.Apellidos)
        self.assertEquals(self.socioCorrecto.FechaNacimiento.date(), socio.FechaNacimiento)
    
    def testGetSocioNotExistent(self):
        form = self.generateSocioForm(self.socioCorrecto) # Registro válido
        socioDict = services.signupSocio(form)
        self.assertEquals(1, socioDict['id'])
        self.assertEquals(self.getSocioCode(form), socioDict['code'])

        with self.assertRaises(ValidationError):
            services.getSocio('2')

#---------------------------------------------------------------------------------------------------------------------------------------------------
    def validateSocioVinculation(self):
        form = self.generateSocioForm(self.socioCorrecto) # Registro válido
        socioDict = services.signupSocio(form)
        self.assertEquals(1, socioDict['id'])
        self.assertEquals(self.getSocioCode(form), socioDict['code'])

        socioGot = services.validateSocioVinculation(socioDict['id'], socioDict['code'])
        self.assertEquals(socioGot.id, socioDict['id'])
        self.assertEquals(socioGot.CodigoSocio, self.getSocioCode(form))

        with self.assertRaises(ValidationError): #Caso de código no correspondiente al socio
            services.validateSocioVinculation(socioDict['id'], 'CNV0001')

        with self.assertRaises(ValidationError): #Caso de id no existente
            services.validateSocioVinculation(5, socioDict['code'])


#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testValidateUserDataDifferentPassword(self):
            form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=True)
            with self.assertRaises(services.SeveralErrorMessagesException):
                services.validateUserData(form)


    def testValidateUserDataTlf(self):

        #completo con prefijo
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, tlf= "(+34) 638 326 891")
        self.assertTrue(services.validateUserData(form))

        # prefijo sin parentesis
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, tlf="+34 638 326 891")
        self.assertTrue(services.validateUserData(form))

        # todo junto con prefijo
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, tlf="+34638326891")
        self.assertTrue(services.validateUserData(form))

        # sin prefijo
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, tlf="638 326 891")
        self.assertTrue(services.validateUserData(form))

        # sin espaciado
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, tlf="638326891")
        self.assertTrue(services.validateUserData(form))

        #------- ERROR CASES -------

        #Inicio incorrecto
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, tlf="123 456 789")
        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validateUserData(form)

        #Muy largo
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, tlf="623 456 7891")
        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validateUserData(form)

        #Muy corto
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, tlf="623 456")
        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validateUserData(form)

        #Mal prefijo
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, tlf="+1234 981 456 789")
        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validateUserData(form)

        #Mal espaciado
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, tlf="623 45 67 89")
        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validateUserData(form)

    def testValidateUserDataCP(self):
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False)
        self.assertTrue(services.validateUserData(form))

        #------- ERROR CASES -------

        # muy corto
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, cp="123")
        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validateUserData(form)

        # muy largo
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, cp="123456789")
        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validateUserData(form)
        
        # con letras
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, cp="1234q")
        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validateUserData(form)

    #---------------------------------------------------------------------------------------------------------------------------------------------------
    def testCompleteUserForm(self):
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True) # Registro válido
        (user, userPassword) = services.completeUserForm(form, RolUsuario.USUARIO)
        self.assertIsNotNone(user)
        self.assertEquals(user.email, self.tutorCorrecto.email)
        self.assertEquals(user.user_role, RolUsuario.USUARIO)
        self.assertTrue(user.check_password(userPassword))

        self.tutorCorrecto.email = 'email1@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick1'
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True) # Registro válido
        (user, userPassword) = services.completeUserForm(form, RolUsuario.TESORERIA)
        self.assertIsNotNone(user)
        self.assertEquals(user.email, self.tutorCorrecto.email)
        self.assertEquals(user.user_role, RolUsuario.TESORERIA)
        self.assertTrue(user.check_password(userPassword))

        self.tutorCorrecto.email = 'email2@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick2'
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True) # Registro válido
        (user, userPassword) = services.completeUserForm(form, RolUsuario.AMIGO)
        self.assertIsNotNone(user)
        self.assertEquals(user.email, self.tutorCorrecto.email)
        self.assertEquals(user.user_role, RolUsuario.AMIGO)
        self.assertTrue(user.check_password(userPassword))

        self.tutorCorrecto.email = 'email3@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick3'
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True) # Registro válido
        (user, userPassword) = services.completeUserForm(form, RolUsuario.PERSONAL)
        self.assertIsNotNone(user)
        self.assertEquals(user.email, self.tutorCorrecto.email)
        self.assertEquals(user.user_role, RolUsuario.PERSONAL)
        self.assertTrue(user.check_password(userPassword))

        self.tutorCorrecto.email = 'email4@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick4'
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True) # Registro válido
        (user, userPassword) = services.completeUserForm(form, RolUsuario.PRESIDENCIA)
        self.assertIsNotNone(user)
        self.assertEquals(user.email, self.tutorCorrecto.email)
        self.assertEquals(user.user_role, RolUsuario.PRESIDENCIA)
        self.assertTrue(user.check_password(userPassword))

        self.tutorCorrecto.email = 'email5@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick5'
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True) # Registro válido
        (user, userPassword) = services.completeUserForm(form, RolUsuario.SECRETARIA)
        self.assertIsNotNone(user)
        self.assertEquals(user.email, self.tutorCorrecto.email)
        self.assertEquals(user.user_role, RolUsuario.SECRETARIA)
        self.assertTrue(user.check_password(userPassword))

        self.tutorCorrecto.email = 'email6@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick6'
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True) # Registro válido
        (user, userPassword) = services.completeUserForm(form, RolUsuario.ADMINISTRADOR)
        self.assertIsNotNone(user)
        self.assertEquals(user.email, self.tutorCorrecto.email)
        self.assertEquals(user.user_role, RolUsuario.ADMINISTRADOR)
        self.assertTrue(user.check_password(userPassword))
    #---------------------------------------------------------------------------------------------------------------------------------------------------
    def testSignupUsuario(self):
        socioform = self.generateSocioForm(self.socioCorrecto) # Registro de socio para asignar como asociado
        dict = services.signupSocio(socioform)

        self.tutorCorrecto.email = 'email1@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick1'
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True) # Registro válido
        (user, userPassword) = services.completeUserForm(form, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user)
        self.assertEquals(user.id, 1)
        self.assertEquals(user.username, self.tutorCorrecto.username)
        self.assertEquals(user.email, self.tutorCorrecto.email)
        self.assertEquals(user.first_name, self.tutorCorrecto.first_name)
        self.assertEquals(user.last_name, self.tutorCorrecto.last_name)
        self.assertEquals(RolUsuario.USUARIO, self.tutorCorrecto.user_role)
        self.assertTrue(user.check_password(userPassword))
        id = services.saveUserProfile(form, idSocio=str(dict['id']), usuarioVincular=user)
        self.assertEquals(id, user.id)

        self.tutorCorrecto.email = 'email2@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick2'
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=False, permImg=False) # Registro válido
        (user, userPassword) = services.completeUserForm(form, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user)
        self.assertEquals(user.id, 2)
        self.assertEquals(user.username, self.tutorCorrecto.username)
        self.assertEquals(user.email, self.tutorCorrecto.email)
        self.assertEquals(user.first_name, self.tutorCorrecto.first_name)
        self.assertEquals(user.last_name, self.tutorCorrecto.last_name)
        self.assertEquals(RolUsuario.USUARIO, self.tutorCorrecto.user_role)
        self.assertTrue(user.check_password(userPassword))
        id = services.saveUserProfile(form, idSocio=str(dict['id']), usuarioVincular=user)
        self.assertEquals(id, user.id)

        self.amigoCorrecto.email = 'email3@email.com'
        self.amigoCorrecto.username = 'amigoCorrectonick1'
        amigoform = self.generateUserForm(self.amigoCorrectoProfile, invalidPwd=False, isAmigo=True, Notificar=True, permImg=False) # registro válido sin socio b. asociado (caso de amigo)
        (user, userPassword) = services.completeUserForm(amigoform, RolUsuario.AMIGO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user)
        self.assertEquals(user.id, 3)
        self.assertEquals(user.username, self.amigoCorrecto.username)
        self.assertEquals(user.email, self.amigoCorrecto.email)
        self.assertEquals(user.first_name, self.amigoCorrecto.first_name)
        self.assertEquals(user.last_name, self.amigoCorrecto.last_name)
        self.assertEquals(RolUsuario.AMIGO, self.amigoCorrecto.user_role)
        self.assertTrue(user.check_password(userPassword))
        id = services.saveUserProfile(amigoform, idSocio=None, usuarioVincular=user)
        self.assertEquals(id, user.id)

        self.amigoCorrecto.email = 'email4@email.com'
        self.amigoCorrecto.username = 'amigoCorrectonick2'
        amigoform = self.generateUserForm(self.amigoCorrectoProfile, invalidPwd=False, isAmigo=True, Notificar=False, permImg=False) # registro válido sin socio b. asociado (caso de amigo)
        (user, userPassword) = services.completeUserForm(amigoform, RolUsuario.AMIGO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user)
        self.assertEquals(user.id, 4)
        self.assertEquals(user.username, self.amigoCorrecto.username)
        self.assertEquals(user.email, self.amigoCorrecto.email)
        self.assertEquals(user.first_name, self.amigoCorrecto.first_name)
        self.assertEquals(user.last_name, self.amigoCorrecto.last_name)
        self.assertEquals(RolUsuario.AMIGO, self.amigoCorrecto.user_role)
        self.assertTrue(user.check_password(userPassword))
        id = services.saveUserProfile(amigoform, idSocio=None, usuarioVincular=user)
        self.assertEquals(id, user.id)

    def testSignupUsuarioOptionalField(self):
        socioform = self.generateSocioForm(self.socioCorrecto) # Registro de socio para asignar como asociado
        dict = services.signupSocio(socioform)

        self.tutorCorrecto.Provincia = None
        self.assertIsNone(self.tutorCorrecto.Provincia)
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False) # Registro válido con opcional vacío
        (user, userPassword) = services.completeUserForm(form, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        id = services.saveUserProfile(form, idSocio=str(dict['id']), usuarioVincular=user)
        self.assertEquals(1, id)
    #---------------------------------------------------------------------------------------------------------------------------------------------------
    def testGetUserByIdentifiers(self):
        #--- INICIALIZACION  DB ---
        socioform = self.generateSocioForm(self.socioCorrecto) # Registro de socio para asignar como asociado
        dict = services.signupSocio(socioform)

        self.tutorCorrecto.email = 'email1@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick1'
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True) # Registro válido
        (user1, userPassword) = services.completeUserForm(form, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user1)
        id = services.saveUserProfile(form, idSocio=str(dict['id']), usuarioVincular=user1)
        self.assertEquals(id, user1.id)

        self.tutorCorrecto.email = 'email2@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick2'
        form = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=False, permImg=False) # Registro válido
        (user2, userPassword) = services.completeUserForm(form, RolUsuario.AMIGO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user2)
        id = services.saveUserProfile(form, idSocio=None, usuarioVincular=user2)
        self.assertEquals(id, user2.id)

        # --- BY ID: TEST CASES ---
        
        userGot = services.getUserById(userId=1)
        self.assertEquals(userGot.id, 1)
        self.assertEquals(userGot.email, user1.email)
        self.assertEquals(userGot.first_name, user1.first_name)
        self.assertEquals(userGot.last_name, user1.last_name)
        self.assertEquals(userGot.user_role, user1.user_role)

        userGot = services.getUserById(userId=2)
        self.assertEquals(userGot.id, 2)
        self.assertEquals(userGot.email, user2.email)
        self.assertEquals(userGot.first_name, user2.first_name)
        self.assertEquals(userGot.last_name, user2.last_name)
        self.assertEquals(userGot.user_role, user2.user_role)

        # --- ERROR CASES ---

        with self.assertRaises(ValidationError):
            services.getUserById(userId=5) #ID no existe

        with self.assertRaises(ValidationError):
            services.getUserById(userId='patata') #ID no válido

    #---------------------------------------------------------------------------------------------------------------------------------------------------

        # --- BY E-MAIL: TEST CASES ---
        
        userGot = services.getUserByEmail(userEmail='email1@email.com')
        self.assertEquals(userGot.id, 1)
        self.assertEquals(userGot.email, user1.email)
        self.assertEquals(userGot.first_name, user1.first_name)
        self.assertEquals(userGot.last_name, user1.last_name)
        self.assertEquals(userGot.user_role, user1.user_role)

        userGot = services.getUserByEmail(userEmail='email2@email.com')
        self.assertEquals(userGot.id, 2)
        self.assertEquals(userGot.email, user2.email)
        self.assertEquals(userGot.first_name, user2.first_name)
        self.assertEquals(userGot.last_name, user2.last_name)
        self.assertEquals(userGot.user_role, user2.user_role)

        # --- ERROR CASES ---
        with self.assertRaises(ValidationError):
            services.getUserByEmail(userEmail='emailNotExists@email.com')

        with self.assertRaises(ValidationError):
            services.getUserByEmail(userEmail='notAnEmail')
        
        # --- BY NICKNAME: TEST CASES ---

        userGot = services.getUserByNick(username='tutorCorrectonick1')
        self.assertEquals(userGot.id, 1)
        self.assertEquals(userGot.email, user1.email)
        self.assertEquals(userGot.first_name, user1.first_name)
        self.assertEquals(userGot.last_name, user1.last_name)
        self.assertEquals(userGot.user_role, user1.user_role)

        userGot = services.getUserByNick(username='tutorCorrectonick2')
        self.assertEquals(userGot.id, 2)
        self.assertEquals(userGot.email, user2.email)
        self.assertEquals(userGot.first_name, user2.first_name)
        self.assertEquals(userGot.last_name, user2.last_name)
        self.assertEquals(userGot.user_role, user2.user_role)

        # --- ERROR CASES ---
        with self.assertRaises(ValidationError):
            services.getUserByNick(username='emailNotExists@email.com')

    #---------------------------------------------------------------------------------------------------------------------------------------------------
    def testgetUserProfile(self):
        #--- INICIALIZACION  DB ---
        socioform = self.generateSocioForm(self.socioCorrecto) # Registro de socio para asignar como asociado
        dict = services.signupSocio(socioform)

        socio = services.getSocio(idSocio=dict['id'])

        self.tutorCorrecto.email = 'email1@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick1'
        form1 = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True, tlf='687446235') # Registro válido
        (user1, userPassword) = services.completeUserForm(form1, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user1)
        id = services.saveUserProfile(form1, idSocio=str(dict['id']), usuarioVincular=user1)
        self.assertEquals(id, user1.id)

        self.tutorCorrecto.email = 'email2@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick2'
        form2 = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=False, permImg=False, tlf='687446235') # Registro válido
        (user2, userPassword) = services.completeUserForm(form2, RolUsuario.AMIGO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user2)
        id = services.saveUserProfile(form2, idSocio=None, usuarioVincular=user2)
        self.assertEquals(id, user2.id)

        # --- TEST CASES ---

        profileGot = services.getUserProfile(userId=1)
        self.assertEquals(str(profileGot.Telefono), form1.cleaned_data['telefono'])
        self.assertEquals(profileGot.Direccion, form1.cleaned_data['direccion'])
        self.assertEquals(str(profileGot.CodigoPostal), form1.cleaned_data['codPostal'])
        self.assertEquals(profileGot.Localidad, form1.cleaned_data['localidad'])
        self.assertEquals(profileGot.Provincia, form1.cleaned_data['provincia'])
        self.assertEquals(profileGot.Asociado, socio)
        self.assertEquals(profileGot.UserVinculado, user1)
        self.assertEquals(profileGot.Relacion, form1.cleaned_data['relSocio'])
        self.assertEquals(profileGot.Notificar, form1.cleaned_data['notificar'])
        self.assertEquals(profileGot.PermisoImagen, form1.cleaned_data['permisoImg'])
        self.assertEquals(profileGot.AceptaUsoDatos, form1.cleaned_data['usoDatos'])

        profileGot = services.getUserProfile(userId=2)
        self.assertEquals(str(profileGot.Telefono), form2.cleaned_data['telefono'])
        self.assertEquals(profileGot.Direccion, form2.cleaned_data['direccion'])
        self.assertEquals(str(profileGot.CodigoPostal), form2.cleaned_data['codPostal'])
        self.assertEquals(profileGot.Localidad, form2.cleaned_data['localidad'])
        self.assertEquals(profileGot.Provincia, form2.cleaned_data['provincia'])
        self.assertEquals(profileGot.UserVinculado, user2)
        self.assertEquals(profileGot.Notificar, form2.cleaned_data['notificar'])
        self.assertEquals(profileGot.PermisoImagen, form2.cleaned_data['permisoImg'])
        self.assertEquals(profileGot.AceptaUsoDatos, form2.cleaned_data['usoDatos'])
        self.assertIsNone(profileGot.Asociado)
        self.assertIsNone(profileGot.Relacion)

        # --- ERROR CASES ---

        with self.assertRaises(ValidationError):
            services.getUserProfile(userId=5) #ID no existe

        with self.assertRaises(ValidationError):
            services.getUserProfile(userId='patata') #ID no válido

        
    #---------------------------------------------------------------------------------------------------------------------------------------------------
    def testgetAsociado(self):
        #--- INICIALIZACION  DB ---
        socioform = self.generateSocioForm(self.socioCorrecto) # Registro de socio para asignar como asociado
        dict = services.signupSocio(socioform)

        socio = services.getSocio(idSocio=dict['id'])

        self.tutorCorrecto.email = 'email1@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick1'
        form1 = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True, tlf='687446235') # Registro válido
        (user1, userPassword) = services.completeUserForm(form1, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user1)
        id = services.saveUserProfile(form1, idSocio=str(dict['id']), usuarioVincular=user1)
        self.assertEquals(id, user1.id)

        self.tutorCorrecto.email = 'email2@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick2'
        form2 = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=False, permImg=False, tlf='687446235') # Registro válido
        (user2, userPassword) = services.completeUserForm(form2, RolUsuario.AMIGO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user2)
        id = services.saveUserProfile(form2, idSocio=None, usuarioVincular=user2)
        self.assertEquals(id, user2.id)

        # --- TEST CASES ---

        asociado = services.getAsociado(idUser=1)
        self.assertEquals(asociado.id, socio.id)
        self.assertEquals(asociado.Nombre, socio.Nombre)
        self.assertEquals(asociado.Apellidos, socio.Apellidos)
        self.assertEquals(asociado.FechaNacimiento, socio.FechaNacimiento)

        asociado = services.getAsociado(idUser=2)
        self.assertIsNone(asociado)

        # --- ERROR CASES ---

        with self.assertRaises(ValidationError):
            services.getAsociado(idUser=5) #ID no existe

        with self.assertRaises(ValidationError):
            services.getAsociado(idUser='patata') #ID no válido
    #---------------------------------------------------------------------------------------------------------------------------------------------------
    def testValidateBank(self):
        #--- INICIALIZACION  DB ---
        socioform = self.generateSocioForm(self.socioCorrecto)
        dict = services.signupSocio(socioform)

        socio = services.getSocio(idSocio=dict['id'])
        #generar fichero
        f = None
        filename = './demoSEPAfileGenerated.txt'
        try: 
            f = open(filename, "a")
            f.write("This is a \n SEPA FILE trial with \n some lines in it.")
        except FileExistsError:
            f = open(filename, 'rb')
        f.close()
        self.assertIsNotNone(f)

        # --- TEST CASES ---

        bankForm = self.generateBankForm(filename='./demoSEPAfileGenerated.txt', isAmigo=False, tarifa=87.56)
        self.assertTrue(services.validateBank(bankForm, socio, self.minAmigo))

        bankForm = self.generateBankForm(filename='./demoSEPAfileGenerated.txt', isAmigo=True, tarifa=87.56)
        if bankForm.is_valid():
            self.assertTrue(services.validateBank(bankForm, None, self.minAmigo))

        # --- ERROR CASES ---

        with self.assertRaises(services.SeveralErrorMessagesException):#Tarifa negativa
            bankForm = self.generateBankForm(filename=filename, isAmigo=True, tarifa=-5.55)
            self.assertTrue(services.validateBank(bankForm, None, self.minAmigo))

        with self.assertRaises(services.SeveralErrorMessagesException):#Tarifa 0
            bankForm = self.generateBankForm(filename=filename, isAmigo=True, tarifa=0)
            self.assertTrue(services.validateBank(bankForm, None, self.minAmigo))

        with self.assertRaises(services.SeveralErrorMessagesException):# IBAN muy largo
            bankForm = self.generateBankForm(filename=filename, iban='ES7100302053091234567895193847', isAmigo=True, tarifa=87.56)
            self.assertTrue(services.validateBank(bankForm, None, self.minAmigo))
        
        with self.assertRaises(services.SeveralErrorMessagesException):# IBAN muy corto
            bankForm = self.generateBankForm(filename=filename, iban='ES710030205', isAmigo=False, tarifa=87.56)
            self.assertTrue(services.validateBank(bankForm, socio, self.minAmigo))

        with self.assertRaises(services.SeveralErrorMessagesException):# IBAN sin letras
            bankForm = self.generateBankForm(filename=filename, iban='127100302053091234567895', isAmigo=False, tarifa=87.56)
            self.assertTrue(services.validateBank(bankForm, socio, self.minAmigo))

        os.remove("./demoSEPAfileGenerated.txt")
    #---------------------------------------------------------------------------------------------------------------------------------------------------
    def testValidateHasBankInfo(self):
        self.assertFalse(services.hasBankInfo(self.socioCorrecto))

        self.socioCorrecto.IBAN = 'ES71003020530912345'
        self.assertTrue(services.hasBankInfo(self.socioCorrecto))

        self.socioCorrecto.TitularIBAN = 'Name'
        self.assertTrue(services.hasBankInfo(self.socioCorrecto))

        self.socioCorrecto.SEPA = '/path/to/SEPA'
        self.assertTrue(services.hasBankInfo(self.socioCorrecto))

        self.socioCorrecto.Tarifa = 87.65
        self.assertTrue(services.hasBankInfo(self.socioCorrecto))
    #---------------------------------------------------------------------------------------------------------------------------------------------------
    def testSignupBank(self):
        socioform = self.generateSocioForm(self.socioCorrecto)
        dict = services.signupSocio(socioform)

        self.tutorCorrecto.email = 'email1@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick1'
        form1 = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True, tlf='687446235') # Registro válido
        (user1, userPassword) = services.completeUserForm(form1, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user1)
        id = services.saveUserProfile(form1, idSocio=str(dict['id']), usuarioVincular=user1)
        self.assertEquals(id, user1.id)

        self.tutorCorrecto.email = 'email2@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick2'
        form2 = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=False, permImg=False, tlf='687446235') # Registro válido
        (user2, userPassword) = services.completeUserForm(form2, RolUsuario.AMIGO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user2)
        
        id = services.saveUserProfile(form2, idSocio=None, usuarioVincular=user2)
        self.assertEquals(id, user2.id)

        #crear fichero
        try:
            f = open('./demoSEPAfile.txt', 'x')
            f.write('Contenido del fichero\ncon varias líneas\npara probar el SEPA Bank Form.')
            f.close()
        except FileExistsError:
            f = open('./demoSEPAfile.txt', 'rb')
        bankform = self.generateBankForm(filename='./demoSEPAfile.txt')
        if bankform.is_valid():
            id = services.signupBankData(bankform=bankform, userId=user1.id, minAmigo=self.minAmigo)
            self.assertEquals(user1.id, id)
            socio = services.getAsociado(user1.id)
            self.assertEquals(socio.TitularIBAN, bankform.cleaned_data['titular'])
            self.assertEquals(socio.IBAN, bankform.cleaned_data['iban'])
            self.assertIsNotNone(socio.SEPA)
        
        os.remove('./demoSEPAfile.txt')

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testSignupHospital(self):
        form = self.generateSocioForm(self.socioCorrecto) # Registro válido de socio
        socioDict = services.signupSocio(form)
        self.assertEquals(1, socioDict['id'])
        self.assertEquals(self.getSocioCode(form), socioDict['code'])

        socio = services.getSocio(1)

        hospFormData = {
            'nombre': self.tutorCorrecto.first_name,
            'localidad': self.tutorCorrecto.last_name,
            'provincia': self.tutorCorrecto.first_name,
        }
        hospForm = HospitalForm(hospFormData)
        if hospForm.is_valid():#validación predeterminada llega, se debe hacer por separado
            services.signupHospital(hospForm=hospForm, socio=socio)
        else:
            self.assertTrue(False)

        hosp = Hospitales.objects.get(Nombre=hospFormData['nombre'])
        self.assertIsNotNone(hosp)
        self.assertEquals(hosp.Nombre, hospFormData['nombre'])
        self.assertEquals(hosp.Localidad, hospFormData['localidad'])
        self.assertEquals(hosp.Provincia, hospFormData['provincia'])

        hospA = HospitalizaA.objects.get(Socio=socio)
        self.assertIsNotNone(hospA)
        self.assertEquals(hospA.Hospital, hosp)
        self.assertEquals(hospA.Socio, socio)

        with self.assertRaises(ValidationError): #Volver a registrar un usuario ya registrado
            services.signupHospital(hospForm=hospForm, socio=socio)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testSignupOptData(self):
        #--- INICIALIZACION  DB ---
        socioform = self.generateSocioForm(self.socioCorrecto) # Registro de socio para asignar como asociado
        dict = services.signupSocio(socioform)

        socio = services.getSocio(idSocio=dict['id'])

        self.tutorCorrecto.email = 'email1@email.com'
        self.tutorCorrecto.username = 'tutorCorrectonick1'
        form1 = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True, tlf='687446235') # Registro válido
        (user1, userPassword) = services.completeUserForm(form1, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user1)
        id = services.saveUserProfile(form1, idSocio=str(dict['id']), usuarioVincular=user1)
        self.assertEquals(id, user1.id)

        # --- TEST CASES ---

        hospFormData = {
            'nombre': self.tutorCorrecto.first_name,
            'localidad': self.tutorCorrecto.last_name,
            'provincia': self.tutorCorrecto.first_name,
        }
        hospForm = HospitalForm(hospFormData)
        if hospForm.is_valid(): #validación predeterminada llega, se debe hacer por separado
            services.signupOptData(hospForm, user1.id, 'Hospitales')
        else:
            self.assertTrue(False)

        hosp = Hospitales.objects.get(Nombre=hospFormData['nombre'])
        self.assertIsNotNone(hosp)
        self.assertEquals(hosp.Nombre, hospFormData['nombre'])
        self.assertEquals(hosp.Localidad, hospFormData['localidad'])
        self.assertEquals(hosp.Provincia, hospFormData['provincia'])

        hospA = HospitalizaA.objects.get(Socio=socio)
        self.assertIsNotNone(hospA)
        self.assertEquals(hospA.Hospital, hosp)
        self.assertEquals(hospA.Socio, socio)

        # --- ERROR CASES ---

        with self.assertRaises(ValidationError): #Volver a registrar un hospital ya registrado
            services.signupOptData(hospForm, user1.id, 'Hospitales')

        with self.assertRaises(ValidationError): #registrar entidad que no existe
            services.signupOptData(hospForm, user1.id, 'patatas')

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testChangeUserPassword(self):
        #--- INICIALIZACION  DB ---
        socioform = self.generateSocioForm(self.socioCorrecto) # Registro de socio para asignar como asociado
        dict = services.signupSocio(socioform)

        socio = services.getSocio(idSocio=dict['id'])

        self.tutorCorrecto.email = 'emailPwdChange@email.com'
        self.tutorCorrecto.username = 'nickPwdChange'
        form1 = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True, tlf='687446235') # Registro válido
        (user1, userPassword) = services.completeUserForm(form1, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user1)
        id = services.saveUserProfile(form1, idSocio=str(dict['id']), usuarioVincular=user1)
        self.assertEquals(id, user1.id)

        # --- TEST CASES ---

        self.assertFalse(user1.check_password('HolaGente65'))

        pwdFormData = {
            'password1': 'HolaGente65',
            'password2': 'HolaGente65',
        }
        pwdForm = PasswordForm(pwdFormData)
        newPwd = services.changeUserPassword(pwdForm, user1.email)
        user = Users.objects.get(id=user1.id) #dato cambiado, hay que volver a traerlo de la BD
        self.assertTrue(user.check_password('HolaGente65'))

        # --- ERROR CASES ---

        with self.assertRaises(ValidationError): #contraseñas no coinciden
            pwdFormData = {
                'password1': 'HolaGente65',
                'password2': 'NoCoindido',
            }
            pwdForm = PasswordForm(pwdFormData)
            services.changeUserPassword(pwdForm, user1.email)

        with self.assertRaises(ValidationError): #Email que no corresponde a ningún usuario
            pwdFormData = {
                'password1': 'HolaGente65',
                'password2': 'HolaGente65',
            }
            pwdForm = PasswordForm(pwdFormData)
            services.changeUserPassword(pwdForm, 'noexiste@email.com')

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testKeepsStaff(self):
        #--- INICIALIZACION  DB ---
        socioform = self.generateSocioForm(self.socioCorrecto) # Registro de socio para asignar como asociado
        dict = services.signupSocio(socioform)

        form1 = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True, tlf='687446235') # Registro válido
        (user1, userPassword) = services.completeUserForm(form1, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user1)
        id = services.saveUserProfile(form1, idSocio=str(dict['id']), usuarioVincular=user1)
        self.assertEquals(id, user1.id)

        # --- TEST CASES ---

        self.assertFalse(services.keepsStaff(user1.id))
        user1.is_staff = True
        user1.save()
        self.assertTrue(services.keepsStaff(user1.id))

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testAddLog(self):
        #--- INICIALIZACION  DB ---
        socioform = self.generateSocioForm(self.socioCorrecto) # Registro de socio para asignar como asociado
        dict = services.signupSocio(socioform)

        form1 = self.generateUserForm(self.tutorCorrectoProfile, invalidPwd=False, Notificar=True, permImg=True, tlf='687446235') # Registro válido
        (user1, userPassword) = services.completeUserForm(form1, RolUsuario.USUARIO) # Establecer el rol de usuario correcto
        self.assertIsNotNone(user1)
        id = services.saveUserProfile(form1, idSocio=str(dict['id']), usuarioVincular=user1)
        self.assertEquals(id, user1.id)

        loginTime = timezone.now()

        # --- TEST CASES ---

        user1.last_login = loginTime
        user1.save()

        services.addLog(user1)

        logInstance = AccessLog.objects.get(User=user1)
        self.assertIsNotNone(logInstance)
        self.assertEquals(logInstance.User, user1)
        self.assertEquals(logInstance.Login.strftime('%d-%m-%Y %H:%M:%S'), loginTime.strftime('%d-%m-%Y %H:%M:%S'))
        self.assertTrue(logInstance.Login < logInstance.Logout < timezone.now())



