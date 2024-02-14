from django.test import TransactionTestCase
from datetime import datetime
from login.models import Socios, Users, UserProfiles, Hospitales, HospitalizaA, AmigoBank, AccessLog
from login.constants import Relaciones, RolUsuario


from django.db.utils import IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model

class testModel(TransactionTestCase):
    reset_sequences = True # evitar confilctos de ids autogenerados entre test cases
    nick = 'PruebaNick66'
    name = 'PruebaMan'
    aps = 'Apellidos Apellidos'
    socioCode = 'LPR2000'
    direccion = 'una direccion de prueba'
    tlf = '646545343'
    cp = 15330
    loc = 'Localidad'
    date = datetime.strptime('19/09/22', '%d/%m/%y')
    iban = '341122223333444455556666'
    validEmail = 'prueba@email.com'
    invalidEmail = 'notValid'
    hashPwd = b'$2b$12$E3/Cr7gZrvDq4Q59DA6Nh.R8f7tYhHc6xrkCBg1CCLjW7wjGVJzQG'
    passwd = 'holaMundo'
    sepa = 'path/al/documento/sepa.pdf'
    tarifa = 20.55
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testBeforeWritingInDB(self): # Test de probar a buscar una entrada antes de escribirla en la Base de Datos
        with self.assertRaises(Socios.DoesNotExist):
            socioInstance = Socios(
                Nombre=self.name,
                CodigoSocio=self.socioCode,
                Apellidos=self.aps,
                FechaNacimiento=self.date,
                IBAN=self.iban,
                TitularIBAN = self.name,
            )
            Socios.objects.get(Nombre=self.name) # aún no guardado en la base de datos, debe saltar una excepción

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testAddToDB(self): # Test de añadir una entrada de datos a cada Base de Datos
        # ---------- Socios ---------------
        socioInstance = Socios(
                Nombre=self.name,
                CodigoSocio=self.socioCode,
                Apellidos=self.aps,
                FechaNacimiento=self.date,
                IBAN=self.iban,
                TitularIBAN = self.name,
                SEPA = self.sepa,
            )
        socioInstance.save() # acción de guardar en la base de datos
        entry = Socios.objects.get(Nombre=self.name)
        self.assertIsNotNone(entry) # Comprobar que existe una entrada en la base de datos con el nombre
        self.assertEquals(entry.id, 1)
        self.assertEquals(entry.Nombre, self.name)
        self.assertEquals(entry.CodigoSocio, self.socioCode)
        self.assertEquals(entry.Apellidos, self.aps)
        self.assertEquals(entry.FechaNacimiento.strftime('%d/%m/%y'), self.date.strftime('%d/%m/%y')) 
        self.assertEquals(entry.IBAN, self.iban)
        self.assertEquals(entry.TitularIBAN, self.name)
        self.assertEquals(entry.SEPA, self.sepa) # Comprobar que los atributos están bien introducidos
        # ---------- APARTADO USUARIOS ---------------
        # ---------- Users ---------------

        userInstance = Users(
            email=self.validEmail,
            first_name=self.name,
            last_name=self.aps,
            user_role=RolUsuario.USUARIO,
            password=self.passwd,
            is_staff=False,
            is_active=True,
            is_superuser=False,
            date_joined=timezone.now(),
            incomplete=False,
            )
        userInstance.save() # acción de guardar en la base de datos
        userEntry = Users.objects.get(email=self.validEmail)
        self.assertIsNotNone(entry) # Comprobar que existe una entrada en la base de datos con el nombre

        self.assertEquals(userEntry.email, self.validEmail)
        self.assertEquals(userEntry.first_name, self.name)
        self.assertEquals(userEntry.last_name, self.aps)
        self.assertEquals(userEntry.user_role, RolUsuario.USUARIO)
        self.assertEquals(userEntry.password, self.passwd)
        self.assertFalse(userEntry.is_staff)
        self.assertFalse(userEntry.is_superuser)
        self.assertTrue(userEntry.is_active)
        self.assertFalse(userEntry.incomplete)
        self.assertEquals(userEntry.date_joined.strftime('%d/%m/%y'), datetime.now().strftime('%d/%m/%y'))

        # ---------- UserProfiles ---------------
        profInstance = UserProfiles(
            Telefono = self.tlf,
            Direccion = self.direccion,
            CodigoPostal = self.cp,
            Localidad = self.loc,
            Provincia = self.loc,
            Asociado = entry,
            UserVinculado = userEntry,
            Relacion = Relaciones.PATERNAL, 
            Notificar = True,
            PermisoImagen = True,
            AceptaUsoDatos = True,
        )
        profInstance.save() # acción de guardar en la base de datos
        profEntry = UserProfiles.objects.get(UserVinculado=userEntry)
        self.assertIsNotNone(profEntry)

        self.assertEquals(profEntry.Telefono, int(self.tlf))
        self.assertEquals(profEntry.Direccion, self.direccion)
        self.assertEquals(profEntry.CodigoPostal, self.cp)
        self.assertEquals(profEntry.Localidad, self.loc)
        self.assertEquals(profEntry.Provincia, self.loc)
        self.assertEquals(profEntry.Relacion, Relaciones.PATERNAL)
        self.assertEquals(profEntry.Asociado.id, entry.id)
        self.assertEquals(profEntry.UserVinculado.email, userEntry.email)
        self.assertTrue(profEntry.Notificar)
        self.assertTrue(profEntry.PermisoImagen)
        self.assertTrue(profEntry.AceptaUsoDatos) #endProblem

        # ---------- Hospitales ---------------
        hopInstance = Hospitales(
            Nombre=self.name,
            Localidad=self.loc,
            Provincia=self.direccion,
            )
        hopInstance.save() # acción de guardar en la base de datos
        hopEntry = Hospitales.objects.get(Nombre=self.name)
        self.assertIsNotNone(hopEntry) # Comprobar que existe una entrada en la base de datos con el nombre
        self.assertEquals(hopEntry.id, 1)
        self.assertEquals(hopEntry.Nombre, self.name)
        self.assertEquals(hopEntry.Localidad, self.loc)
        self.assertEquals(hopEntry.Provincia, self.direccion)
        # ---------- HospitalizaA ---------------
        haInstance = HospitalizaA(Hospital=hopEntry, Socio=entry)
        haInstance.save()
        haEntry = HospitalizaA.objects.get(Hospital=hopEntry, Socio=entry)
        self.assertIsNotNone(haEntry)
        self.assertEquals(haEntry.id, 1)
        self.assertEquals(haEntry.Hospital, hopEntry)
        self.assertEquals(haEntry.Socio, entry)
        self.assertEquals(haEntry.Tvi.strftime('%d/%m/%y'), datetime.now().strftime('%d/%m/%y'))
        self.assertIsNone(haEntry.Tvf)
        # ---------- AmigoBank ---------------
        abInstance = AmigoBank(
            UserVinculado = userEntry,
            IBAN = self.iban,
            TitularIBAN = self.name,
            SEPA = self.sepa,
        )
        abInstance.save()
        abEntry = AmigoBank.objects.get(UserVinculado = userEntry, IBAN = abInstance.IBAN, TitularIBAN = abInstance.TitularIBAN, SEPA = abInstance.SEPA,)
        self.assertIsNotNone(abEntry)
        self.assertEquals(abEntry.UserVinculado, userEntry)
        self.assertEquals(abEntry.IBAN, self.iban)
        self.assertEquals(abEntry.TitularIBAN, self.name)
        self.assertEquals(abEntry.SEPA, self.sepa)
        self.assertFalse(abEntry.PagoRegistrado)
        # ---------- AccessLog ---------------
        dateTimeValue = timezone.now()
        alInstance = AccessLog(
            User = userEntry,
            Login = dateTimeValue,
            Logout = dateTimeValue,
        )
        alInstance.save()
        alEntry = AccessLog.objects.get(User=userEntry)
        self.assertIsNotNone(alEntry)
        self.assertEquals(alEntry.User, userEntry)
        self.assertEquals(alEntry.Login, dateTimeValue)
        self.assertEquals(alEntry.Logout, dateTimeValue)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testComplexPrimaryKeyHospitalizaA(self):
        #--------------INIT---------------
        socioInstance = Socios(Nombre=self.name, Apellidos=self.aps, FechaNacimiento=self.date)
        socioInstance.save() # acción de guardar en la base de datos
        soc1Entry = Socios.objects.get(Nombre=self.name, Apellidos=self.aps, FechaNacimiento=self.date)

        socioInstance2 = Socios(Nombre="otroSocio", Apellidos=self.aps, FechaNacimiento=self.date)
        socioInstance2.save()
        soc2Entry = Socios.objects.get(Nombre="otroSocio", Apellidos=self.aps, FechaNacimiento=self.date)

        hopInstance = Hospitales(Nombre=self.name)
        hopInstance.save() # acción de guardar en la base de datos
        hopEntry = Hospitales.objects.get(Nombre=self.name)

        hopInstance2 = Hospitales(Nombre='L\'Hopital')
        hopInstance2.save() # acción de guardar en la base de datos
        hop2Entry = Hospitales.objects.get(Nombre='L\'Hopital')

        haInstance = HospitalizaA(Hospital=hopEntry, Socio=soc1Entry)
        haInstance.save()
        haEntry = HospitalizaA.objects.get(Hospital=hopEntry, Socio=soc1Entry)
        #------------TEST------------------
        haInstanceValidCase1 = HospitalizaA(Hospital=hopEntry, Socio=soc2Entry)
        haInstanceValidCase1.save()
        haEntry2 = HospitalizaA.objects.get(Hospital=hopEntry, Socio=soc2Entry)
        self.assertIsNotNone(haEntry2)
        self.assertEquals(haEntry2.Hospital, hopEntry)
        self.assertEquals(haEntry2.Socio, soc2Entry)

        haInstanceValidCase2 = HospitalizaA(Hospital=hop2Entry, Socio=soc1Entry)
        haInstanceValidCase2.save()
        haEntry3 = HospitalizaA.objects.get(Hospital=hop2Entry, Socio=soc1Entry)
        self.assertIsNotNone(haEntry3)
        self.assertEquals(haEntry3.Hospital, hop2Entry)
        self.assertEquals(haEntry3.Socio, soc1Entry)

        haInstanceDuplicateCase = HospitalizaA(Hospital=hopEntry, Socio=soc1Entry, Tvi=haEntry.Tvi) # caso duplicado con mismo Tiempo de inicio
        with self.assertRaises(IntegrityError):
            haInstanceDuplicateCase.save()

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testCreateUserWithManager(self):
        user = get_user_model().objects.create_user(username=self.nick, email=self.validEmail, password=self.passwd)
        user.save()
        userData = Users.objects.get(email=self.validEmail)

        self.assertEquals(userData.email, self.validEmail)
        self.assertEquals(userData.username, self.nick)
        self.assertTrue(userData.check_password(self.passwd))
        self.assertFalse(userData.is_superuser)
        self.assertFalse(userData.is_staff)
        self.assertTrue(userData.is_active)
        self.assertTrue(userData.incomplete) #faltan datos bancarios, debe ser True
        self.assertEquals(userData.user_role, RolUsuario.AMIGO)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testCreateUserWithName(self):
        user = get_user_model().objects.create_user(username=self.nick, email=self.validEmail, first_name=self.name, last_name=self.aps, password=self.passwd, is_staff=True)
        user.save()
        userData = Users.objects.get(email=self.validEmail)

        self.assertEquals(userData.email, self.validEmail)
        self.assertEquals(userData.username, self.nick)
        self.assertEquals(userData.first_name, self.name)
        self.assertEquals(userData.last_name, self.aps)
        self.assertTrue(userData.check_password(self.passwd))
        self.assertFalse(userData.is_superuser)
        self.assertTrue(userData.is_staff)
        self.assertTrue(userData.is_active)
        self.assertTrue(userData.incomplete) #faltan datos bancarios, debe ser True
        self.assertEquals(userData.user_role, RolUsuario.AMIGO)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testCreateSuperuserWithManager(self):
        user = get_user_model().objects.create_superuser(username=self.nick, email=self.validEmail, password=self.passwd)
        user.save()
        userData = Users.objects.get(email=self.validEmail)

        self.assertEquals(userData.email, self.validEmail)
        self.assertEquals(userData.username, self.nick)
        self.assertTrue(userData.check_password(self.passwd))
        self.assertTrue(userData.is_superuser)
        self.assertTrue(userData.is_staff)
        self.assertTrue(userData.is_active)
        self.assertFalse(userData.incomplete) #EL superusuario es especial, está completo sin datos bancarios
        self.assertEquals(userData.user_role, RolUsuario.ADMINISTRADOR)

        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_superuser(username=self.nick, email=self.validEmail, password=self.passwd, is_superuser=False)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testCreateSuperuserWithName(self):
        user = get_user_model().objects.create_superuser(username=self.nick, email=self.validEmail, first_name=self.name, last_name=self.aps, password=self.passwd)
        user.save()
        userData = Users.objects.get(email=self.validEmail)

        self.assertEquals(userData.email, self.validEmail)
        self.assertEquals(userData.username, self.nick)
        self.assertEquals(userData.first_name, self.name)
        self.assertEquals(userData.last_name, self.aps)
        self.assertTrue(userData.check_password(self.passwd))
        self.assertTrue(userData.is_superuser)
        self.assertTrue(userData.is_staff)
        self.assertTrue(userData.is_active)
        self.assertFalse(userData.incomplete) #EL superusuario es especial, está completo sin datos bancarios
        self.assertEquals(userData.user_role, RolUsuario.ADMINISTRADOR)