from django.test import TransactionTestCase

from notificaciones import services
from notificaciones import models
from notificaciones.constants import NoticeScope
from notificaciones.forms import newNoticeForm
from login.models import Users
from login.constants import RolUsuario

class testServices(TransactionTestCase):
    reset_sequences = True # evitar confilctos de ids autogenerados entre test cases

    newTitulo = 'Nueva Notice'
    newTexto = 'Nuevo texto \n en varias lineas \n para una notice de prueba'

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

    secretario = Users(
        username= 'secretarionick',
        email='secretario@email.com',
        first_name='secretario',
        last_name='Apellidos secretario',
        user_role=RolUsuario.SECRETARIA,
        incomplete=False,
        is_active=True,
        is_staff=True,
    )

    tesorero = Users(
        username= 'tesoreronick',
        email='tesorero@email.com',
        first_name='tesorero',
        last_name='Apellidos tesorero',
        user_role=RolUsuario.TESORERIA,
        incomplete=False,
        is_active=True,
        is_staff=True,
    )

    secreNotice = models.Notice(
            Creador = secretario,
            Destino = NoticeScope.PERSONAL,
            Titulo = 'secreNotice',
            Texto = 'texto en \n varias líneas.',
            Adjunto = None,
            #FechaCreacion = timezone.now(),
        )

    tesoNotice = models.Notice(
            Creador = tesorero,
            Destino = NoticeScope.TODOS,
            Titulo = 'tesoNotice',
            Texto = 'texto en \n varias líneas.',
            Adjunto = None,
            #FechaCreacion = timezone.now(),
        )
    
    def setUpDB(self):
        self.tutor.save()
        self.secretario.save()
        self.tesorero.save()

        self.secreNotice.save()
        self.tesoNotice.save()

        users = Users.objects.all().count()
        notices = models.Notice.objects.all().count()

        self.assertEquals(users, 3)
        self.assertEquals(notices, 2)

#---------------------------------------------------------------------------------------------------------------------------------------------------
#                                                           T E S T S
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetNoticeById(self):
        self.setUpDB()

        #------- TEST CASES -------

        notice = services.getNoticeById(1)

        self.assertEquals(notice.Creador, self.secreNotice.Creador)
        self.assertEquals(notice.Destino, self.secreNotice.Destino)
        self.assertEquals(notice.Titulo, self.secreNotice.Titulo)
        self.assertEquals(notice.Texto, self.secreNotice.Texto)

        #--------------------------

        notice = services.getNoticeById(2)

        self.assertEquals(notice.Creador, self.tesoNotice.Creador)
        self.assertEquals(notice.Destino, self.tesoNotice.Destino)
        self.assertEquals(notice.Titulo, self.tesoNotice.Titulo)
        self.assertEquals(notice.Texto, self.tesoNotice.Texto)


#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetAllNotices(self):
        self.setUpDB()

        #------- TEST CASES -------
        #vista de usuario raso
        (notices, vistos) = services.getAllNotices(self.tutor)

        self.assertIsNotNone(notices)
        self.assertEquals(notices[0], self.tesoNotice)
        self.assertEquals(list(vistos), [])

        #--------------------------

        (notices, vistos) = services.getAllNotices(self.tesorero)
        #vista de staff
        self.assertIsNotNone(notices)
        self.assertEquals(len(notices), 2)
        self.assertEquals(list(vistos), [])

        #--------------------------
        vistoNuevo = models.Vistos(
            Notice = self.tesoNotice, 
            User = self.tutor,
        )

        vistoNuevo.save()

        (notices, vistos) = services.getAllNotices(self.tutor)

        self.assertIsNotNone(notices)
        self.assertEquals(vistos[0], self.tesoNotice.id) #comprobar que se devuelve una lista de los vistos por el usuario

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testSendNotice(self):
        self.setUpDB()

        #------- TEST CASES -------

        noticeData = {
            'titulo': self.newTitulo,
            'texto': self.newTexto,
            'adjunto': None,
            'destino': NoticeScope.TODOS,
        }

        noticeForm = newNoticeForm(noticeData)

        self.assertTrue(noticeForm.is_valid())

        services.sendNotice(noticeForm, self.secretario)

        noticeInstance = models.Notice.objects.get(Creador=self.secretario, Titulo=self.newTitulo)
        self.assertIsNotNone(noticeInstance)

        self.assertEquals(noticeInstance.Creador, self.secretario)
        self.assertEquals(noticeInstance.Destino, noticeData['destino'])
        self.assertEquals(noticeInstance.Titulo, noticeData['titulo'])
        self.assertEquals(noticeInstance.Texto, noticeData['texto'])

        #--------------------------

        noticeData = {
            'titulo': 'otherNotice',
            'texto': self.newTexto,
            'adjunto': None,
            'destino': NoticeScope.PERSONAL,
        }
        noticeForm = newNoticeForm(noticeData)

        self.assertTrue(noticeForm.is_valid())

        services.sendNotice(noticeForm, self.secretario)

        noticeInstance = models.Notice.objects.get(Creador=self.secretario, Titulo='otherNotice')
        self.assertIsNotNone(noticeInstance)

        self.assertEquals(noticeInstance.Creador, self.secretario)
        self.assertEquals(noticeInstance.Destino, noticeData['destino'])
        self.assertEquals(noticeInstance.Titulo, noticeData['titulo'])
        self.assertEquals(noticeInstance.Texto, noticeData['texto'])

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testUpdateViewed(self):
        self.setUpDB()

        #------- TEST CASES -------

        services.updateViewed(self.secreNotice.id, self.secretario)

        vista = models.Vistos.objects.get(Notice=self.secreNotice, User=self.secretario)
        self.assertIsNotNone(vista)

        #--------------------------

        services.updateViewed(self.secreNotice.id, self.tesorero)

        vistas = models.Vistos.objects.filter(Notice=self.secreNotice)
        self.assertIsNotNone(vistas)
        self.assertEquals(vistas.count(), 2)

        services.updateViewed(self.secreNotice.id, self.tesorero) #comprobar que varias llamadas dejan el estado consistente

        vistas = models.Vistos.objects.filter(Notice=self.secreNotice)
        self.assertIsNotNone(vistas)
        self.assertEquals(vistas.count(), 2)


#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetPendantNotices(self):
        self.setUpDB()

        #------- TEST CASES -------

        pendant = services.getPendantNotices(self.secretario)
        self.assertEquals(pendant, 2)
        services.updateViewed(self.secreNotice.id, self.secretario)
        pendant = services.getPendantNotices(self.secretario)

        self.assertEquals(pendant, 1)

        services.updateViewed(self.tesoNotice.id, self.secretario)
        pendant = services.getPendantNotices(self.secretario)

        self.assertEquals(pendant, 0)


        #--------------------------

        pendant = services.getPendantNotices(self.tutor)

        self.assertEquals(pendant, 1)

        services.updateViewed(self.tesoNotice.id, self.tutor)
        pendant = services.getPendantNotices(self.tutor)

        self.assertEquals(pendant, 0)

#---------------------------------------------------------------------------------------------------------------------------------------------------