from datetime import datetime

from django.test import TransactionTestCase

from login import services
from login.models import Socios, Users, UserProfiles
from login.constants import RolUsuario, Relaciones


class testServices(TransactionTestCase):
    reset_sequences = True # evitar confilctos de ids autogenerados entre test cases

    socio = Socios(
        Nombre='socioPrueba',
        Apellidos='Aps socioPrueba',
        FechaNacimiento=datetime.strptime('19/09/22', '%d/%m/%y'),
        CodigoSocio= 's1',
        IBAN = 'ES7100302053091234567895',
        TitularIBAN = 'TitularIBAN',
        SEPA = '/path/to/sepa.pdf',
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

    tutorNoNotice = Users(
        username= 'tutorNoNotice',
        email='tutorNoNotice@email.com',
        first_name='TutorPrueba',
        last_name='Apellidos tutorPrueba',
        user_role=RolUsuario.USUARIO,
        incomplete=False,
        is_active=True,
        is_staff=False,
    )

    tutorNoNoticeProfile = UserProfiles(
        Telefono = 687446235,
        Direccion = 'alguna direccion de prueba',
        CodigoPostal='15340',
        Localidad = 'A Coruña',
        Provincia = 'A Coruña',
        Asociado = socio,
        UserVinculado = tutorNoNotice,
        Relacion = Relaciones.PATERNAL,
        Notificar = False,
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

    amigoNoNotice = Users(
        username= 'amigoNoNotice',
        email='amigoNoNotice@email.com',
        first_name='AmigoPrueba',
        last_name='Apellidos amigoPrueba',
        user_role=RolUsuario.AMIGO, 
        incomplete=False,
        is_active=True,
        is_staff=False,
    )

    amigoNoNoticeProfile = UserProfiles(
        Telefono = 987653487,
        Direccion = 'alguna direccion de prueba',
        CodigoPostal='15221',
        Localidad = 'A Coruña',
        Provincia = 'A Coruña',
        Asociado = None,
        UserVinculado = amigoNoNotice,
        Relacion = None,
        Notificar = False,
        PermisoImagen = False,
        AceptaUsoDatos = True,
    )

    def setUpDB(self):
        self.socio.save()

        self.tutor.save()
        self.tutorNoNotice.save()
        self.amigo.save()
        self.amigoNoNotice.save()

        self.tutorProfile.save()
        self.tutorNoNoticeProfile.save()
        self.amigoProfile.save()
        self.amigoNoNoticeProfile.save()

        sociosCount = Socios.objects.all().count()
        usersCount = Users.objects.all().count()
        userProfCount = UserProfiles.objects.all().count()

        self.assertEquals(first=sociosCount,second=1)
        self.assertEquals(first=usersCount, second=4)
        self.assertEquals(first=userProfCount, second=4)



#---------------------------------------------------------------------------------------------------------------------------------------------------
#                                                           T E S T S
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetNotices(self):
        self.setUpDB()

        #------- TEST CASES -------

        self.assertTrue(services.getNotices(user=self.tutor))
        self.assertTrue(services.getNotices(user=self.amigo))
        self.assertFalse(services.getNotices(user=self.tutorNoNotice))
        self.assertFalse(services.getNotices(user=self.amigoNoNotice))