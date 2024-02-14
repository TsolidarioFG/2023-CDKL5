from datetime import datetime

from django.test import TransactionTestCase

from login import models as lm
from dataManagement import models as dmm
from dataManagement import services
from dataManagement.forms import payVarsForm
from login.constants import RolUsuario, Relaciones

class testServices(TransactionTestCase):
    reset_sequences = True # evitar confilctos de ids autogenerados entre test cases

    socio = lm.Socios(
        Nombre='socioPrueba',
        Apellidos='Aps socioPrueba',
        FechaNacimiento=datetime.strptime('19/09/22', '%d/%m/%y'),
        CodigoSocio= 's1',
        IBAN = 'ES7100302053091234567895',
        TitularIBAN = 'TitularIBAN',
        SEPA = '/path/to/sepa.pdf',
        PagoRegistrado = False,
    )

    socioStaff = lm.Socios(
        Nombre='socioStaff',
        Apellidos='Aps socioStaff',
        FechaNacimiento=datetime.strptime('10/06/22', '%d/%m/%y'),
        CodigoSocio= 's2',
        IBAN = 'ES7100302053091234567892',
        TitularIBAN = 'TitularIBAN',
        SEPA = '/path/to/sepa.pdf',
        PagoRegistrado = True,
    )

    tutor = lm.Users(
        username= 'tutorCorrectonick',
        email='emailtutor@email.com',
        first_name='TutorPrueba',
        last_name='Apellidos tutorPrueba',
        user_role=RolUsuario.USUARIO,
        incomplete=False,
        is_active=True,
        is_staff=False,
    )

    tutorProfile = lm.UserProfiles(
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

    secretario = lm.Users(
        username= 'secretarionick',
        email='secretario@email.com',
        first_name='secretario',
        last_name='Apellidos secretario',
        user_role=RolUsuario.SECRETARIA,
        incomplete=False,
        is_active=True,
        is_staff=True,
    )

    secretarioProfile = lm.UserProfiles(
        Telefono = 685223198,
        Direccion = 'alguna direccion de prueba',
        CodigoPostal='15341',
        Localidad = 'A Coruña',
        Provincia = 'A Coruña',
        Asociado = socioStaff,
        UserVinculado = secretario,
        Relacion = Relaciones.PATERNAL,
        Notificar = True,
        PermisoImagen = True,
        AceptaUsoDatos = True,
    )

    tesorero = lm.Users(
        username= 'tesoreronick',
        email='tesorero@email.com',
        first_name='tesorero',
        last_name='Apellidos tesorero',
        user_role=RolUsuario.TESORERIA,
        incomplete=False,
        is_active=True,
        is_staff=True,
    )

    tesoreroProfile = lm.UserProfiles(
        Telefono = 981422334,
        Direccion = 'alguna direccion de prueba',
        CodigoPostal='15342',
        Localidad = 'A Coruña',
        Provincia = 'A Coruña',
        Asociado = socioStaff,
        UserVinculado = tesorero,
        Relacion = Relaciones.HERMANDAD,
        Notificar = True,
        PermisoImagen = True,
        AceptaUsoDatos = True,
    )

    amigo = lm.Users(
        username= 'amigoCorrectonick',
        email='emailamigo@email.com',
        first_name='AmigoPrueba',
        last_name='Apellidos amigoPrueba',
        user_role=RolUsuario.AMIGO, 
        incomplete=False,
        is_active=True,
        is_staff=False,
    )

    amigoProfile = lm.UserProfiles(
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

    amigoBank = lm.AmigoBank(
        UserVinculado = amigo,
        IBAN = 'ES7100302053091234567894',
        TitularIBAN = 'AmigoTitular',
        SEPA = '/path/to/sepa.pdf',
        Tarifa = 20.00,
        PagoRegistrado = False,
    )

    macros = dmm.Macros(
        TarifaSocios = 36,
        MinimoAmigos = 20,
        diaCobro = 15,
        mesCobro = 4,
    )

    def setUpDB(self):
        self.socio.save() # socios
        self.socioStaff.save()

        self.tutor.save() # usuarios
        self.secretario.save()
        self.tesorero.save()
        self.amigo.save()

        self.tutorProfile.save() # perfiles de usuario
        self.secretarioProfile.save()
        self.tesoreroProfile.save()
        self.amigoProfile.save()

        self.amigoBank.save() #datos bancarios de amigos

        self.macros.save() # constantes persistentes

        sociosCount = lm.Socios.objects.all().count()
        usersCount = lm.Users.objects.all().count()
        userProfCount = lm.UserProfiles.objects.all().count()
        amigoBankCount = lm.AmigoBank.objects.all().count()
        macrosCount = dmm.Macros.objects.all().count()

        self.assertEquals(first=sociosCount,second=2)
        self.assertEquals(first=usersCount, second=4)
        self.assertEquals(first=userProfCount, second=4)
        self.assertEquals(first=amigoBankCount, second=1)
        self.assertEquals(first=macrosCount, second=1)

#---------------------------------------------------------------------------------------------------------------------------------------------------
#                                                           T E S T S
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetPaginatedSecretaryList(self):
        self.setUpDB()

        #------- TEST CASES -------

        pages = services.getPaginatedSecretaryList(itemsPerPage=5, searchQuery=None) #unica pagina, sin busqueda
        self.assertIsNotNone(pages)
        self.assertEquals(pages.num_pages, 1)
        page_obj = pages.page(1)

        self.assertEquals(len(page_obj.object_list), 4)

        for object in page_obj.object_list: #comprobar datos
            if object.Rol == RolUsuario.USUARIO:
                self.assertEquals(object.Email, self.tutor.email)
                self.assertEquals(object.Nombre, self.tutor.first_name)
                self.assertEquals(object.Apellidos, self.tutor.last_name)
                self.assertEquals(object.Socio, self.tutorProfile.Asociado.CodigoSocio)

            if object.Rol == RolUsuario.SECRETARIA:
                self.assertEquals(object.Email, self.secretario.email)
                self.assertEquals(object.Nombre, self.secretario.first_name)
                self.assertEquals(object.Apellidos, self.secretario.last_name)
                self.assertEquals(object.Socio, self.secretarioProfile.Asociado.CodigoSocio)

            if object.Rol == RolUsuario.TESORERIA:
                self.assertEquals(object.Email, self.tesorero.email)
                self.assertEquals(object.Nombre, self.tesorero.first_name)
                self.assertEquals(object.Apellidos, self.tesorero.last_name)
                self.assertEquals(object.Socio, self.tesoreroProfile.Asociado.CodigoSocio)

            if object.Rol == RolUsuario.AMIGO:
                self.assertEquals(object.Email, self.amigo.email)
                self.assertEquals(object.Nombre, self.amigo.first_name)
                self.assertEquals(object.Apellidos, self.amigo.last_name)

        #--------------------------

        pages = services.getPaginatedSecretaryList(itemsPerPage=2, searchQuery=None) # varias paginas, sin busqueda
        self.assertIsNotNone(pages)
        self.assertEquals(pages.num_pages, 2)
        page_obj = pages.page(1)

        self.assertEquals(len(page_obj.object_list), 2)
        self.assertTrue(page_obj.has_next())
        page_obj = pages.page(page_obj.next_page_number())

        self.assertEquals(len(page_obj.object_list), 2)

        #--------------------------

        pages = services.getPaginatedSecretaryList(itemsPerPage=4, searchQuery=self.tutor.email) #buscar por email
        page_obj = pages.page(1)
        self.assertEquals(page_obj.object_list[0].Email, self.tutor.email)
        self.assertEquals(page_obj.object_list[0].Rol, self.tutor.user_role)
        self.assertEquals(page_obj.object_list[0].Nombre, self.tutor.first_name)
        self.assertEquals(page_obj.object_list[0].Apellidos, self.tutor.last_name)

        #--------------------------

        pages = services.getPaginatedSecretaryList(itemsPerPage=4, searchQuery=self.secretario.first_name) #buscar por nombre
        page_obj = pages.page(1)
        self.assertEquals(page_obj.object_list[0].Email, self.secretario.email)
        self.assertEquals(page_obj.object_list[0].Rol, self.secretario.user_role)
        self.assertEquals(page_obj.object_list[0].Nombre, self.secretario.first_name)
        self.assertEquals(page_obj.object_list[0].Apellidos, self.secretario.last_name)

        #--------------------------

        pages = services.getPaginatedSecretaryList(itemsPerPage=4, searchQuery='teso') #buscar por apellido (sin introducirlo completo)
        page_obj = pages.page(1)
        self.assertEquals(page_obj.object_list[0].Email, self.tesorero.email)
        self.assertEquals(page_obj.object_list[0].Rol, self.tesorero.user_role)
        self.assertEquals(page_obj.object_list[0].Nombre, self.tesorero.first_name)
        self.assertEquals(page_obj.object_list[0].Apellidos, self.tesorero.last_name)

        #--------------------------

        pages = services.getPaginatedSecretaryList(itemsPerPage=4, searchQuery='noexisto') #buscar por query que no existe
        self.assertEquals(pages.count, 0)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetPaginatedTreasuryList(self):
        self.setUpDB()

        #------- TEST CASES -------

        pages = services.getPaginatedTreasuryList(itemsPerPage=4, tarifaSocios=36, resetPays=False) #una pagina, sin reset de pagos registrados
        self.assertEquals(pages.num_pages, 1)
        page_obj = pages.page(1)

        self.assertEquals(len(page_obj.object_list), 3)

        for object in page_obj.object_list: #comprobar datos
            if 'SOC' in object.Identificador:
                self.assertTrue(object.IdentificadorShow in [self.socio.CodigoSocio, self.socioStaff.CodigoSocio])
                self.assertEquals(object.Tarifa, 36)
                if object.IdentificadorShow == self.socio.CodigoSocio:
                    self.assertEquals(object.Titular, self.socio.TitularIBAN)
                    self.assertEquals(object.IBAN, self.socio.IBAN)
                    self.assertEquals(object.Pendiente, self.socio.PagoRegistrado)
                if object.IdentificadorShow == self.socioStaff.CodigoSocio:
                    self.assertEquals(object.Titular, self.socioStaff.TitularIBAN)
                    self.assertEquals(object.IBAN, self.socioStaff.IBAN)
                    self.assertEquals(object.Pendiente, self.socioStaff.PagoRegistrado)

            if 'AMG' in object.Identificador:
                self.assertEquals(object.IdentificadorShow, self.amigo.email)
                self.assertEquals(object.Titular, self.amigoBank.TitularIBAN)
                self.assertEquals(object.IBAN, self.amigoBank.IBAN)
                self.assertEquals(object.Tarifa, self.amigoBank.Tarifa)
                self.assertEquals(object.Pendiente, self.amigoBank.PagoRegistrado)

        #--------------------------

        pages = services.getPaginatedTreasuryList(itemsPerPage=2, tarifaSocios=36, resetPays=False) #varias paginas
        self.assertEquals(pages.num_pages, 2)
        page_obj = pages.page(1)

        self.assertEquals(len(page_obj.object_list), 2)
        self.assertTrue(page_obj.has_next)
        page_obj = pages.page(page_obj.next_page_number())

        self.assertEquals(len(page_obj.object_list), 1)

        #--------------------------

        pages = services.getPaginatedTreasuryList(itemsPerPage=5, tarifaSocios=36, resetPays=True) #Resetear pagos registrados

        page_obj = pages.page(1)
        for object in page_obj.object_list: #comprobar datos
            self.assertFalse(object.Pendiente)


#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetAllUserData(self):
        self.setUpDB()

        #------- TEST CASES -------

        (sepaPath, userNick, datalist) = services.getAllUserData(self.tutorProfile.id) #buscar tutor con socio
        self.assertEquals(sepaPath, self.tutorProfile.Asociado.SEPA)
        self.assertEquals(userNick, self.tutor.username)

        for (title, form) in datalist:
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

        (sepaPath, userNick, datalist) = services.getAllUserData(self.amigoProfile.id) #buscar Amigo
        self.assertEquals(sepaPath, self.amigoBank.SEPA)
        self.assertEquals(userNick, self.amigo.username)

        for (title, form) in datalist:
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
                self.assertEquals(form['tarifa'].value(), self.amigoBank.Tarifa)
                
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetGeneralVars(self):
        self.setUpDB()

        #------- TEST CASES -------

        dataDict = services.getGeneralVars()

        self.assertEquals(dataDict['minAmigo'], self.macros.MinimoAmigos)
        self.assertEquals(dataDict['tarSocio'], self.macros.TarifaSocios)
        self.assertEquals(dataDict['payDate'].strftime('%d-%m'), str(self.macros.diaCobro) + '-' + str(self.macros.mesCobro).zfill(2))


#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testValidatePayForm(self):
        self.setUpDB()

        #------- TEST CASES -------

        payFormData = {
            'minAmigo': self.macros.MinimoAmigos,
            'tarSocio': self.macros.TarifaSocios,
            'payDate': datetime.strptime('15-10-23', '%d-%m-%y'),
        }

        payForm = payVarsForm(payFormData)

        self.assertTrue(services.validatePayForm(payForm))

        #------- ERROR CASES -------

        payFormData = { #minimo amigos no valido
            'minAmigo': -1,
            'tarSocio': self.macros.TarifaSocios,
            'payDate': datetime.strptime('15-10-23', '%d-%m-%y'),
        }

        payForm = payVarsForm(payFormData)

        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validatePayForm(payForm)

        #--------------------------

        payFormData = { #tarifa de socios no valida
            'minAmigo': self.macros.MinimoAmigos,
            'tarSocio': -1,
            'payDate': datetime.strptime('15-10-23', '%d-%m-%y'),
        }

        payForm = payVarsForm(payFormData)

        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validatePayForm(payForm)

        #--------------------------

        payFormData = { #fecha no valida
            'minAmigo': self.macros.MinimoAmigos,
            'tarSocio': self.macros.TarifaSocios,
            'payDate': 'novalido',
        }

        payForm = payVarsForm(payFormData)

        with self.assertRaises(services.SeveralErrorMessagesException):
            services.validatePayForm(payForm)

        #--------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testUpdateGeneralVars(self):
        self.setUpDB()

        macros = dmm.Macros.objects.all().last()

        self.assertEquals(macros.MinimoAmigos, self.macros.MinimoAmigos)
        self.assertEquals(macros.TarifaSocios, self.macros.TarifaSocios)
        self.assertEquals(macros.diaCobro, self.macros.diaCobro)
        self.assertEquals(macros.mesCobro, self.macros.mesCobro)

        #------- TEST CASES -------

        payFormData = {
            'minAmigo': 45.20,
            'tarSocio': 30.436,
            'payDate': datetime.strptime('09-10-23', '%d-%m-%y'),
        }

        payForm = payVarsForm(payFormData)

        services.updateGeneralVars(payForm)

        macrosNew = dmm.Macros.objects.all().last()

        self.assertEquals(macrosNew.MinimoAmigos, 45.20)
        self.assertEquals(macrosNew.TarifaSocios, 30.44) #comprobar redondeo a los dos decimales
        self.assertEquals(macrosNew.diaCobro, 9)
        self.assertEquals(macrosNew.mesCobro, 10)

        #------- ERROR CASES -------

        payFormData = { #minimo amigos no valido
            'minAmigo': -1,
            'tarSocio': self.macros.TarifaSocios,
            'payDate': datetime.strptime('15-10-23', '%d-%m-%y'),
        }

        payForm = payVarsForm(payFormData)

        with self.assertRaises(services.SeveralErrorMessagesException):
            services.updateGeneralVars(payForm)

        #--------------------------

        payFormData = { #tarifa de socios no valida
            'minAmigo': self.macros.MinimoAmigos,
            'tarSocio': -1,
            'payDate': datetime.strptime('15-10-23', '%d-%m-%y'),
        }

        payForm = payVarsForm(payFormData)

        with self.assertRaises(services.SeveralErrorMessagesException):
            services.updateGeneralVars(payForm)

        #--------------------------

        payFormData = { #fecha no valida
            'minAmigo': self.macros.MinimoAmigos,
            'tarSocio': self.macros.TarifaSocios,
            'payDate': 'novalido',
        }

        payForm = payVarsForm(payFormData)

        with self.assertRaises(services.SeveralErrorMessagesException):
            services.updateGeneralVars(payForm)

#---------------------------------------------------------------------------------------------------------------------------------------------------
