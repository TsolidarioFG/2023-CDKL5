from datetime import datetime
from django.utils import timezone

from django.test import TransactionTestCase

from login.models import Socios, Users, UserProfiles, AmigoBank, Hospitales, HospitalizaA
from login.constants import RolUsuario, Relaciones
from login import services
from login.services import ValidationError, SeveralErrorMessagesException
from login.forms import UserModForm, TutorProfileForm, AmigoProfileForm, AmigoBankModForm, SocioModForm, SocioBankModForm


class testServices(TransactionTestCase):
    reset_sequences = True # evitar confilctos de ids autogenerados entre test cases

    socio = Socios(
        Nombre='socioPrueba',
        Apellidos='Aps socioPrueba',
        FechaNacimiento=datetime.strptime('19/09/22', '%d/%m/%y'),
        CodigoSocio= 's1',
        IBAN = 'ES7100302053091234567895',
        TitularIBAN = 'TitularIBAN',
        SEPA = '',
        PagoRegistrado = False,
    )

    socioOrphan = Socios(
        Nombre='socioOrphan',
        Apellidos='Aps Huerfanos',
        FechaNacimiento=datetime.strptime('19/09/22', '%d/%m/%y'),
        CodigoSocio= 'sH',
        IBAN = 'ES7100302053091234567895',
        TitularIBAN = 'TitularIBAN',
        SEPA = '',
        PagoRegistrado = False,
    )

    tutor = Users(
        username= 'tutorCorrectonick',
        email='emailtutor@email.com',
        first_name='TutorPrueba',
        last_name='Apellidos tutorPrueba',
        user_role=RolUsuario.USUARIO,
        incomplete=False,
        is_active=True,
        is_staff=False,
    )

    tutorProfile = UserProfiles(
        Telefono = 687446235,
        Direccion = 'alguna direccion de prueba',
        CodigoPostal='15340',
        Localidad = 'A Coruña',
        Provincia = 'A Coruña',
        Asociado = socio,
        UserVinculado = tutor,
        Relacion = Relaciones.PATERNAL,
        Notificar = True,
        PermisoImagen = True,
        AceptaUsoDatos = True,
    )

    amigo = Users(
        username= 'amigoCorrectonick',
        email='emailamigo@email.com',
        first_name='AmigoPrueba',
        last_name='Apellidos amigoPrueba',
        user_role=RolUsuario.AMIGO, 
        incomplete=False,
        is_active=True,
        is_staff=False,
    )

    amigoProfile = UserProfiles(
        Telefono = 987653487,
        Direccion = 'alguna direccion de prueba',
        CodigoPostal='15221',
        Localidad = 'A Coruña',
        Provincia = 'A Coruña',
        Asociado = None,
        UserVinculado = amigo,
        Relacion = None,
        Notificar = True,
        PermisoImagen = False,
        AceptaUsoDatos = True,
    )

    amigoBank = AmigoBank(
        UserVinculado = amigo,
        IBAN = 'ES7100302053091234567894',
        TitularIBAN = 'AmigoTitular',
        SEPA = '',
        Tarifa = 20.00,
        PagoRegistrado = False,
    )

    hosps = Hospitales(
        Nombre = 'Hospitalensias',
        Localidad = 'LocalHospital',
        Provincia = 'provHosp',
    )

    hospNoVinc = Hospitales(
        Nombre = 'HospitalNoVinculado',
        Localidad = 'LocalHospital',
        Provincia = 'provHosp',
    )

    hospA = HospitalizaA(
        Hospital = hosps, 
        Socio = socio,
        Tvi = datetime.strptime('19/09/22', '%d/%m/%y').date(),
        Tvf = None,
    )

    def generateSEPAFile(self, filename):
        filepath = './media/' + filename
        
        try:
            f = open(filepath, 'x')
            f.write('Contenido del fichero\ncon varias líneas\npara probar el SEPA Bank Form.')
            f.close()
        except FileExistsError:
            f = open(filepath, 'rb')

        return filename

    def setUpDB(self):

        self.socio.save()
        self.socioOrphan.save()

        self.tutor.save()
        self.amigo.save()

        self.tutorProfile.save()
        self.amigoProfile.save()

        self.amigoBank.save()

        self.hosps.save()
        self.hospNoVinc.save()
        
        self.hospA.save()

        sociosCount = Socios.objects.all().count()
        usersCount = Users.objects.all().count()
        userProfCount = UserProfiles.objects.all().count()
        amigoBankCount = AmigoBank.objects.all().count()
        hospCount = Hospitales.objects.all().count()
        hospACount = HospitalizaA.objects.all().count()

        self.assertEquals(sociosCount, 2)
        self.assertEquals(usersCount, 2)
        self.assertEquals(userProfCount, 2)
        self.assertEquals(amigoBankCount, 1)
        self.assertEquals(hospCount, 2)
        self.assertEquals(hospACount, 1)


#---------------------------------------------------------------------------------------------------------------------------------------------------
#                                                           T E S T S
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetHospLists(self):
        self.setUpDB()

        #------- TEST CASES -------

        lists = services.getHospLists(self.socio) #socio con vinculaciones
        
        self.assertEquals(lists['all'][0].Nombre, self.hosps.Nombre)
        self.assertEquals(lists['all'][0].Localidad, self.hosps.Localidad)
        self.assertEquals(lists['all'][0].Provincia, self.hosps.Provincia)
        self.assertEquals(lists['all'][1].Nombre, self.hospNoVinc.Nombre)
        self.assertEquals(lists['all'][1].Localidad, self.hospNoVinc.Localidad)
        self.assertEquals(lists['all'][1].Provincia, self.hospNoVinc.Provincia)

        self.assertEquals(lists['vinc'][0], self.hosps.Nombre)

        #--------------------------

        lists = services.getHospLists(self.socioOrphan) #socio sin hospitales vinculados
        
        self.assertEquals(lists['all'][0].Nombre, self.hosps.Nombre)
        self.assertEquals(lists['all'][0].Localidad, self.hosps.Localidad)
        self.assertEquals(lists['all'][0].Provincia, self.hosps.Provincia)
        self.assertEquals(lists['all'][1].Nombre, self.hospNoVinc.Nombre)
        self.assertEquals(lists['all'][1].Localidad, self.hospNoVinc.Localidad)
        self.assertEquals(lists['all'][1].Provincia, self.hospNoVinc.Provincia)

        self.assertEquals(len(lists['vinc']), 0) #QuerySet Vacio

        #--------------------------

        HospitalizaA.objects.all().delete()
        Hospitales.objects.all().delete() #eliminar objetos hospitales

        lists = services.getHospLists(self.socio)

        self.assertEquals(len(lists['all']), 0)
        self.assertEquals(len(lists['vinc']), 0)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testUpdateHospitalVinculation(self):
        self.setUpDB()

        #------- TEST CASES -------

        services.updateHospitalVinc(self.hospNoVinc.Nombre, self.socioOrphan) #vincular un hospital
        haInstance = HospitalizaA.objects.get(Hospital=self.hospNoVinc, Socio=self.socioOrphan)
        self.assertIsNotNone(haInstance)
        self.assertEquals(haInstance.Tvi, timezone.now().date())

        #--------------------------

        services.updateHospitalVinc(self.hosps.Nombre, self.socioOrphan) #vincular un hospital ya vinculado en otro socio

        haInstance = HospitalizaA.objects.get(Hospital=self.hosps, Socio=self.socioOrphan)
        self.assertIsNotNone(haInstance)
        self.assertEquals(haInstance.Tvi, timezone.now().date())

        #--------------------------

        services.updateHospitalVinc(self.hosps.Nombre, self.socio) #desvincular hospital vinculado

        haInstance = HospitalizaA.objects.get(Hospital=self.hosps, Socio=self.socio)
        self.assertIsNotNone(haInstance)
        self.assertEquals(haInstance.Tvi, self.hospA.Tvi)
        self.assertEquals(haInstance.Tvf, timezone.now().date())

        #------- ERROR CASES -------

        with self.assertRaises(ValidationError):
            services.updateHospitalVinc(self.hosps.Nombre, self.socioOrphan) #desvincular hospital recientemente vinculado

            haInstance = HospitalizaA.objects.get(Hospital=self.hosps, Socio=self.socioOrphan)
            self.assertEquals(haInstance.Tvf, timezone.now().date())

            services.updateHospitalVinc(self.hosps.Nombre, self.socioOrphan) #vincular hospital ya vinculado recientemente

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testUpdateVinculations(self):
        self.setUpDB()

        entity = 'hospitals' #entidad a tratar: hospitales

        #------- TEST CASES -------

        prevSelection = [self.hosps.Nombre] #seleccion anterior (Estado inicial: hosps está vinculado)
        newSelection = [self.hosps.Nombre, self.hospNoVinc.Nombre] #Nueva seleccion: Se quiere mantener hosps y vincular hospNoVinc

        services.updateVinculations(prevSelection, newSelection, self.socio, entity) #realizar vinculaciones

        haInstance = HospitalizaA.objects.filter(Socio=self.socio, Tvf=None)
        self.assertEquals(haInstance.count(), 2) #2 hospitales vinculados

        #--------------------------

        prevSelection = [self.hosps.Nombre, self.hospNoVinc.Nombre] #seleccion anterior (Estado inicial: dos hospitales vinculados)
        newSelection = [] #Nueva seleccion: Se quiere desvincular todo

        services.updateVinculations(prevSelection, newSelection, self.socio, entity) #realizar vinculaciones

        haInstance = HospitalizaA.objects.filter(Socio=self.socio, Tvf=None)
        self.assertEquals(haInstance.count(), 0) #no hay hospitales vinculados

        #--------------------------

        prevSelection = [] #seleccion anterior (Estado inicial: sin vinculaciones)
        newSelection = [self.hospNoVinc.Nombre] #Nueva seleccion: Se quiere vincular hospNoVinc

        services.updateVinculations(prevSelection, newSelection, self.socioOrphan, entity) #realizar vinculaciones

        haInstance = HospitalizaA.objects.filter(Socio=self.socioOrphan, Tvf=None)
        self.assertEquals(haInstance.count(), 1) # 1 hospital vinculado
        hospitalVinculado = HospitalizaA.objects.get(Socio=self.socioOrphan, Tvf=None)
        self.assertEquals(hospitalVinculado.Hospital, self.hospNoVinc) #HospNoVinc es el vinculado

        #--------------------------

        prevSelection = [self.hospNoVinc.Nombre] #seleccion anterior (Estado inicial: hospNoVinc vinculado)
        newSelection = [self.hosps.Nombre] #Nueva seleccion: Se quiere desvincular hospNoVinc y a la vez vincular hosps

        services.updateVinculations(prevSelection, newSelection, self.socioOrphan, entity) #realizar vinculaciones

        haInstance = HospitalizaA.objects.filter(Socio=self.socioOrphan, Tvf=None)
        self.assertEquals(haInstance.count(), 1) # 1 hospital vinculado
        hospitalVinculado = HospitalizaA.objects.get(Socio=self.socioOrphan, Tvf=None)
        self.assertEquals(hospitalVinculado.Hospital, self.hosps) #hosps es el vinculado

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testParseGlobalUpdateData(self):
        self.setUpDB()

        #------- TEST CASES -------

        #parse tutor + socio

        data = {
            #User
            'username': self.tutor.username,
            'email': self.tutor.email,
            'first_name': self.tutor.first_name,
            'last_name': self.tutor.last_name,
            'is_staff': self.tutor.is_staff,
            'is_active': self.tutor.is_active,
            'user_role': self.tutor.user_role,
            #UserProfile
            'telefono': self.tutorProfile.Telefono,
            'direccion': self.tutorProfile.Direccion,
            'codPostal': self.tutorProfile.CodigoPostal,
            'localidad': self.tutorProfile.Localidad,
            'provincia': self.tutorProfile.Provincia,
            'relSocio': self.tutorProfile.Relacion,
            'notificar': self.tutorProfile.Notificar,
            'permisoImg': self.tutorProfile.PermisoImagen,
            'usoDatos': self.tutorProfile.AceptaUsoDatos,
            #Socio
            'nombre': self.tutorProfile.Asociado.Nombre,
            'apellidos': self.tutorProfile.Asociado.Apellidos,
            'fechaNac': self.tutorProfile.Asociado.FechaNacimiento,
            #BankData
            'iban': self.tutorProfile.Asociado.IBAN,
            'titular': self.tutorProfile.Asociado.TitularIBAN,
            'sepaDoc': self.tutorProfile.Asociado.SEPA,
        }

        formsDict = services.parseGlobalUpdateData(data, self.socio.SEPA, self.tutor.username)

        self.assertEquals(formsDict['id'], self.tutor.id)

        userForm = formsDict['user']
        userProfForm  = formsDict['profile']
        socioForm = formsDict['socio']
        bankForm = formsDict['bank']

        self.assertEquals(userForm['username'].value(), self.tutor.username)
        self.assertEquals(userForm['email'].value(), self.tutor.email)
        self.assertEquals(userForm['first_name'].value(), self.tutor.first_name)
        self.assertEquals(userForm['last_name'].value(), self.tutor.last_name)
        self.assertEquals(userForm['is_staff'].value(), self.tutor.is_staff)
        self.assertEquals(userForm['is_active'].value(), self.tutor.is_active)
        self.assertEquals(userForm['user_role'].value(), self.tutor.user_role)

        self.assertEquals(userProfForm['telefono'].value(), self.tutorProfile.Telefono)
        self.assertEquals(userProfForm['direccion'].value(), self.tutorProfile.Direccion)
        self.assertEquals(userProfForm['codPostal'].value(), self.tutorProfile.CodigoPostal)
        self.assertEquals(userProfForm['localidad'].value(), self.tutorProfile.Localidad)
        self.assertEquals(userProfForm['provincia'].value(), self.tutorProfile.Provincia)
        self.assertEquals(userProfForm['relSocio'].value(), self.tutorProfile.Relacion)
        self.assertEquals(userProfForm['notificar'].value(), self.tutorProfile.Notificar)
        self.assertEquals(userProfForm['permisoImg'].value(), self.tutorProfile.PermisoImagen)
        self.assertEquals(userProfForm['usoDatos'].value(), self.tutorProfile.AceptaUsoDatos)

        self.assertEquals(socioForm['nombre'].value(), self.tutorProfile.Asociado.Nombre)
        self.assertEquals(socioForm['apellidos'].value(), self.tutorProfile.Asociado.Apellidos)
        self.assertEquals(socioForm['fechaNac'].value(), self.tutorProfile.Asociado.FechaNacimiento)

        self.assertEquals(bankForm['iban'].value(), self.tutorProfile.Asociado.IBAN)
        self.assertEquals(bankForm['titular'].value(), self.tutorProfile.Asociado.TitularIBAN)

        #--------------------------

        #parse amigo


        data = {
            #User
            'username': self.amigo.username,
            'email': self.amigo.email,
            'first_name': self.amigo.first_name,
            'last_name': self.amigo.last_name,
            'is_staff': self.amigo.is_staff,
            'is_active': self.amigo.is_active,
            'user_role': self.amigo.user_role,
            #UserProfile
            'telefono': self.amigoProfile.Telefono,
            'direccion': self.amigoProfile.Direccion,
            'codPostal': self.amigoProfile.CodigoPostal,
            'localidad': self.amigoProfile.Localidad,
            'provincia': self.amigoProfile.Provincia,
            'relSocio': self.amigoProfile.Relacion,
            'notificar': self.amigoProfile.Notificar,
            'permisoImg': self.amigoProfile.PermisoImagen,
            'usoDatos': self.amigoProfile.AceptaUsoDatos,
            #BankData
            'iban': self.amigoBank.IBAN,
            'titular': self.amigoBank.TitularIBAN,
            'sepaDoc': self.amigoBank.SEPA,
        }

        formsDict = services.parseGlobalUpdateData(data, self.amigoBank.SEPA, self.amigo.username)

        self.assertEquals(formsDict['id'], self.amigo.id)

        userForm = formsDict['user']
        userProfForm  = formsDict['profile']
        bankForm = formsDict['bank']

        self.assertEquals(userForm['username'].value(), self.amigo.username)
        self.assertEquals(userForm['email'].value(), self.amigo.email)
        self.assertEquals(userForm['first_name'].value(), self.amigo.first_name)
        self.assertEquals(userForm['last_name'].value(), self.amigo.last_name)
        self.assertEquals(userForm['is_staff'].value(), self.amigo.is_staff)
        self.assertEquals(userForm['is_active'].value(), self.amigo.is_active)
        self.assertEquals(userForm['user_role'].value(), self.amigo.user_role)

        self.assertEquals(userProfForm['telefono'].value(), self.amigoProfile.Telefono)
        self.assertEquals(userProfForm['direccion'].value(), self.amigoProfile.Direccion)
        self.assertEquals(userProfForm['codPostal'].value(), self.amigoProfile.CodigoPostal)
        self.assertEquals(userProfForm['localidad'].value(), self.amigoProfile.Localidad)
        self.assertEquals(userProfForm['provincia'].value(), self.amigoProfile.Provincia)
        self.assertEquals(userProfForm['notificar'].value(), self.amigoProfile.Notificar)
        self.assertEquals(userProfForm['usoDatos'].value(), self.amigoProfile.AceptaUsoDatos)

        self.assertEquals(bankForm['iban'].value(), self.amigoBank.IBAN)
        self.assertEquals(bankForm['titular'].value(), self.amigoBank.TitularIBAN)

        #asegurar que las keys de valores nulos se eliminan

        with self.assertRaises(KeyError):
            userProfForm['relSocio']

        with self.assertRaises(KeyError):
            userProfForm['permisoImg']

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testReallocateData(self):
        self.setUpDB()

        #------- TEST CASES -------

        #tutor + socio

        data = {
            #User
            'username': self.tutor.username,
            'email': self.tutor.email,
            'first_name': self.tutor.first_name,
            'last_name': self.tutor.last_name,
            'is_staff': self.tutor.is_staff,
            'is_active': self.tutor.is_active,
            'user_role': self.tutor.user_role,
            #UserProfile
            'telefono': self.tutorProfile.Telefono,
            'direccion': self.tutorProfile.Direccion,
            'codPostal': self.tutorProfile.CodigoPostal,
            'localidad': self.tutorProfile.Localidad,
            'provincia': self.tutorProfile.Provincia,
            'relSocio': self.tutorProfile.Relacion,
            'notificar': self.tutorProfile.Notificar,
            'permisoImg': self.tutorProfile.PermisoImagen,
            'usoDatos': self.tutorProfile.AceptaUsoDatos,
            #Socio
            'nombre': self.tutorProfile.Asociado.Nombre,
            'apellidos': self.tutorProfile.Asociado.Apellidos,
            'fechaNac': self.tutorProfile.Asociado.FechaNacimiento,
            #BankData
            'iban': self.tutorProfile.Asociado.IBAN,
            'titular': self.tutorProfile.Asociado.TitularIBAN,
            'sepaDoc': self.tutorProfile.Asociado.SEPA,
        }

        formsDict = services.parseGlobalUpdateData(data, self.socio.SEPA, self.tutor.username)

        (file, formList) = services.reallocateData(formsDict)

        self.assertEquals(file, self.tutorProfile.Asociado.SEPA)

        for (title, form) in formList:
            if title == 'Datos Principales del usuario':
                self.assertEquals(form['username'].value(), self.tutor.username)
                self.assertEquals(form['email'].value(), self.tutor.email)
                self.assertEquals(form['first_name'].value(), self.tutor.first_name)
                self.assertEquals(form['last_name'].value(), self.tutor.last_name)
                self.assertEquals(form['user_role'].value(), self.tutor.user_role)
                self.assertEquals(form['is_staff'].value(), self.tutor.is_staff)
                self.assertEquals(form['is_active'].value(), self.tutor.is_active)

            if title == 'Datos Adicionales del Usuario':
                self.assertEquals(form['telefono'].value(), self.tutorProfile.Telefono)
                self.assertEquals(form['direccion'].value(), self.tutorProfile.Direccion)
                self.assertEquals(str(form['codPostal'].value()), self.tutorProfile.CodigoPostal)
                self.assertEquals(form['localidad'].value(), self.tutorProfile.Localidad)
                self.assertEquals(form['provincia'].value(), self.tutorProfile.Provincia)
                self.assertEquals(form['relSocio'].value(), self.tutorProfile.Relacion)
                self.assertEquals(form['notificar'].value(), self.tutorProfile.Notificar)
                self.assertEquals(form['permisoImg'].value(), self.tutorProfile.PermisoImagen)
                self.assertEquals(form['usoDatos'].value(), self.tutorProfile.AceptaUsoDatos)

            if 'Socio Asociado: ' in title:
                self.assertEquals(form['nombre'].value(), self.tutorProfile.Asociado.Nombre)
                self.assertEquals(form['apellidos'].value(), self.tutorProfile.Asociado.Apellidos)
                self.assertEquals(form['fechaNac'].value(), self.tutorProfile.Asociado.FechaNacimiento)

            if title == 'Datos Bancarios del Socio B.:':
                self.assertEquals(form['iban'].value(), self.tutorProfile.Asociado.IBAN)
                self.assertEquals(form['titular'].value(), self.tutorProfile.Asociado.TitularIBAN)

        #--------------------------

        #amigo

        data = {
            #User
            'username': self.amigo.username,
            'email': self.amigo.email,
            'first_name': self.amigo.first_name,
            'last_name': self.amigo.last_name,
            'is_staff': self.amigo.is_staff,
            'is_active': self.amigo.is_active,
            'user_role': self.amigo.user_role,
            #UserProfile
            'telefono': self.amigoProfile.Telefono,
            'direccion': self.amigoProfile.Direccion,
            'codPostal': self.amigoProfile.CodigoPostal,
            'localidad': self.amigoProfile.Localidad,
            'provincia': self.amigoProfile.Provincia,
            'relSocio': self.amigoProfile.Relacion,
            'notificar': self.amigoProfile.Notificar,
            'permisoImg': self.amigoProfile.PermisoImagen,
            'usoDatos': self.amigoProfile.AceptaUsoDatos,
            #BankData
            'iban': self.amigoBank.IBAN,
            'titular': self.amigoBank.TitularIBAN,
            'sepaDoc': self.amigoBank.SEPA,
        }

        formsDict = services.parseGlobalUpdateData(data, self.amigoBank.SEPA, self.amigo.username)

        (file, formList) = services.reallocateData(formsDict)

        self.assertEquals(file, self.amigoBank.SEPA)

        for (title, form) in formList:
            if title == 'Datos Principales del usuario':
                self.assertEquals(form['username'].value(), self.amigo.username)
                self.assertEquals(form['email'].value(), self.amigo.email)
                self.assertEquals(form['first_name'].value(), self.amigo.first_name)
                self.assertEquals(form['last_name'].value(), self.amigo.last_name)
                self.assertEquals(form['user_role'].value(), self.amigo.user_role)
                self.assertEquals(form['is_staff'].value(), self.amigo.is_staff)
                self.assertEquals(form['is_active'].value(), self.amigo.is_active)

            if title == 'Datos Adicionales del Usuario':
                self.assertEquals(form['telefono'].value(), self.amigoProfile.Telefono)
                self.assertEquals(form['direccion'].value(), self.amigoProfile.Direccion)
                self.assertEquals(str(form['codPostal'].value()), self.amigoProfile.CodigoPostal)
                self.assertEquals(form['localidad'].value(), self.amigoProfile.Localidad)
                self.assertEquals(form['provincia'].value(), self.amigoProfile.Provincia)
                self.assertEquals(form['notificar'].value(), self.amigoProfile.Notificar)
                self.assertEquals(form['usoDatos'].value(), self.amigoProfile.AceptaUsoDatos)

            if title == 'Datos Bancarios':
                self.assertEquals(form['iban'].value(), self.amigoBank.IBAN)
                self.assertEquals(form['titular'].value(), self.amigoBank.TitularIBAN)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testValidateUserUpdates(self):
        self.setUpDB()

        #------- TEST CASES -------

        userModData = {
            'username': 'newNickname',
            'email': 'new@email.com',
            'first_name': self.tutor.first_name,
            'last_name': self.tutor.last_name,
            'is_staff': self.tutor.is_staff,
            'is_active': self.tutor.is_active,
            'user_role': self.tutor.user_role,
        }
        userProfModData = {
            'telefono': self.tutorProfile.Telefono,
            'direccion': self.tutorProfile.Direccion,
            'codPostal': self.tutorProfile.CodigoPostal,
            'localidad': self.tutorProfile.Localidad,
            'provincia': self.tutorProfile.Provincia,
            'relSocio': self.tutorProfile.Relacion,
            'notificar': self.tutorProfile.Notificar,
            'permisoImg': self.tutorProfile.PermisoImagen,
            'usoDatos': self.tutorProfile.AceptaUsoDatos,
        }

        userForm = UserModForm(userModData)
        profForm = TutorProfileForm(userProfModData)

        errors = services.validateUserUpdates(userForm, profForm)

        self.assertEquals(len(errors), 0)

        #------- ERROR CASES -------

        userModData['username'] = self.amigo.username #error en userForm

        userForm = UserModForm(userModData)
        profForm = TutorProfileForm(userProfModData)

        errors = services.validateUserUpdates(userForm, profForm)

        self.assertEquals(len(errors), 1)

        #--------------------------

        userProfModData['codPostal'] = 1234 #error en profForm

        userForm = UserModForm(userModData)
        profForm = TutorProfileForm(userProfModData)

        errors = services.validateUserUpdates(userForm, profForm)

        self.assertEquals(len(errors), 2)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testValidateBankUpdates(self):
        self.setUpDB()

        #------- TEST CASES -------

        socioModData = {
            'nombre': self.tutorProfile.Asociado.Nombre,
            'apellidos': self.tutorProfile.Asociado.Apellidos,
            'fechaNac': self.tutorProfile.Asociado.FechaNacimiento,
        }
        bankModData = {
            'iban': self.tutorProfile.Asociado.IBAN,
            'titular': self.tutorProfile.Asociado.TitularIBAN,
            'sepaDoc': self.tutorProfile.Asociado.SEPA,
        }
        abankModData = {
            'iban': self.amigoBank.IBAN,
            'titular': self.amigoBank.TitularIBAN,
            'tarifa': self.amigoBank.Tarifa,
            'sepaDoc': self.amigoBank.SEPA,
        }

        socioForm = SocioModForm(socioModData)
        bankForm = SocioBankModForm(bankModData)
        abankForm = AmigoBankModForm(abankModData)

        errors = services.validateBankUpdates(bankForm, socioForm)

        self.assertEquals(len(errors), 0)

        #--------------------------

        errors = services.validateBankUpdates(abankForm, None)

        self.assertEquals(len(errors), 0)

        #------- ERROR CASES -------

        socioModData['fechaNac'] = 'NOvalgo' #error en socioForm

        socioForm = SocioModForm(socioModData)
        bankForm = SocioBankModForm(bankModData)

        errors = services.validateBankUpdates(bankForm, socioForm)

        self.assertEquals(len(errors), 1)

        #--------------------------

        bankModData['iban'] = '1234' #error en bankForm

        socioForm = SocioModForm(socioModData)
        bankForm = SocioBankModForm(bankModData)

        errors = services.validateBankUpdates(bankForm, socioForm)

        self.assertEquals(len(errors), 2)

        #--------------------------

        abankModData['iban'] = '1234' #error en bankForm
        abankModData['tarifa'] = -1 #error en bankForm

        abankForm = AmigoBankModForm(abankModData)

        errors = services.validateBankUpdates(abankForm, None)

        self.assertEquals(len(errors), 2)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testValidateUserRole(self):
        self.setUpDB()

        #------- TEST CASES -------

        userModData = {
            'username': 'newNickname',
            'email': 'new@email.com',
            'first_name': self.tutor.first_name,
            'last_name': self.tutor.last_name,
            'is_staff': self.tutor.is_staff,
            'is_active': self.tutor.is_active,
            'user_role': self.tutor.user_role,
        }

        userForm = UserModForm(userModData)

        errors = services.validateUserRole(userForm, self.tutorProfile.Asociado)
        
        self.assertEquals(len(errors), 0)

        #------- ERROR CASES -------

        #Usuario sin socio

        errors = services.validateUserRole(userForm, None)
        
        self.assertEquals(len(errors), 2)

        #--------------------------

        #amigo con socio
        userModData['user_role'] = RolUsuario.AMIGO
        userForm = UserModForm(userModData)

        errors = services.validateUserRole(userForm, self.tutorProfile.Asociado)
        
        self.assertEquals(len(errors), 1)

        #--------------------------

        #asignar rol de staff sin tener socio

        userModData['user_role'] = RolUsuario.PRESIDENCIA
        userForm = UserModForm(userModData)

        errors = services.validateUserRole(userForm, None)
        
        self.assertEquals(len(errors), 1)

        userModData['user_role'] = RolUsuario.TESORERIA
        userForm = UserModForm(userModData)

        errors = services.validateUserRole(userForm, None)
        
        self.assertEquals(len(errors), 1)

        userModData['user_role'] = RolUsuario.SECRETARIA
        userForm = UserModForm(userModData)

        errors = services.validateUserRole(userForm, None)
        
        self.assertEquals(len(errors), 1)

        userModData['user_role'] = RolUsuario.PERSONAL
        userForm = UserModForm(userModData)

        errors = services.validateUserRole(userForm, None)
        
        self.assertEquals(len(errors), 1)

        #--------------------------

        #hacer staff sin especificar de que tipo

        userModData['user_role'] = RolUsuario.USUARIO
        userModData['is_staff'] = True
        userForm = UserModForm(userModData)

        errors = services.validateUserRole(userForm, self.tutorProfile.Asociado)
        
        self.assertEquals(len(errors), 1)

        userModData['user_role'] = RolUsuario.AMIGO
        userModData['is_staff'] = True
        userForm = UserModForm(userModData)

        errors = services.validateUserRole(userForm, self.tutorProfile.Asociado)
        
        self.assertEquals(len(errors), 2)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testUpdatePays(self):
        self.setUpDB()

        #------- TEST CASES -------

        #ids en codigo para saber que entidades cambiar (formados en trasuryDisplayObject)
        socioIDChange = 'SOC:' + str(self.socio.id)
        socioOrphanIDChange = 'SOC:' + str(self.socioOrphan.id)

        AmigoBankIDChange = 'AMG:' + str(self.amigo.id)
        #lista de cambios
        updateIDs = [socioIDChange, AmigoBankIDChange] #socio True, socioOrphan False, amigo True

        services.updatePays(updateIDs)

        self.assertTrue(Socios.objects.get(id=self.socio.id).PagoRegistrado)
        self.assertFalse(Socios.objects.get(id=self.socioOrphan.id).PagoRegistrado)
        self.assertTrue(AmigoBank.objects.get(UserVinculado=self.amigo).PagoRegistrado)

        #--------------------------

        updateIDs = [AmigoBankIDChange, socioOrphanIDChange] #socio False, socioOrphan True, amigo True

        services.updatePays(updateIDs)

        self.assertFalse(Socios.objects.get(id=self.socio.id).PagoRegistrado)
        self.assertTrue(Socios.objects.get(id=self.socioOrphan.id).PagoRegistrado)
        self.assertTrue(AmigoBank.objects.get(UserVinculado=self.amigo).PagoRegistrado)

        #--------------------------

        updateIDs = [] #todo a false

        services.updatePays(updateIDs)

        self.assertFalse(Socios.objects.get(id=self.socio.id).PagoRegistrado)
        self.assertFalse(Socios.objects.get(id=self.socioOrphan.id).PagoRegistrado)
        self.assertFalse(AmigoBank.objects.get(UserVinculado=self.amigo).PagoRegistrado)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testDeleteUserData(self):
        self.setUpDB()

        self.socio.SEPA = self.generateSEPAFile('sociosepa.txt')
        self.amigoBank.SEPA = self.generateSEPAFile('amigosepa.txt')

        self.socio.save()
        self.amigoBank.save()

        #------- TEST CASES -------

        services.deleteUserData(self.tutor.id)

        with self.assertRaises(Users.DoesNotExist):
            Users.objects.get(username=self.tutor.username)

        with self.assertRaises(UserProfiles.DoesNotExist):
            UserProfiles.objects.get(UserVinculado=self.tutor)

        with self.assertRaises(Socios.DoesNotExist):
            Socios.objects.get(CodigoSocio=self.socio.CodigoSocio)

        #--------------------------

        services.deleteUserData(self.amigo.id)

        with self.assertRaises(Users.DoesNotExist):
            Users.objects.get(username=self.amigo.username)

        with self.assertRaises(UserProfiles.DoesNotExist):
            UserProfiles.objects.get(UserVinculado=self.amigo)

        with self.assertRaises(AmigoBank.DoesNotExist):
            AmigoBank.objects.get(UserVinculado=self.amigo)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testDeleteOrphanSocios(self):
        self.setUpDB()

        #------- TEST CASES -------

        services.deleteOrphanSocios()

        with self.assertRaises(Socios.DoesNotExist):
            Socios.objects.get(CodigoSocio=self.socioOrphan.CodigoSocio)
            
#---------------------------------------------------------------------------------------------------------------------------------------------------
