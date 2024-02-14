import os

from datetime import datetime
from django.test import TransactionTestCase
from django.utils import timezone
from django.db.utils import IntegrityError

from notificaciones.constants import NoticeScope
from login.models import Users
from notificaciones import models

class testModel(TransactionTestCase):
    reset_sequences = True # evitar confilctos de ids autogenerados entre test cases

    importantDataForUsers = [('email1@email.com', 'username1'), ('email2@email.com', 'username2'), ('email3@email.com', 'usename3')]

    def setup_Users(self): #crear usuarios para hacer de creadores de posts
        userList = []
        for email,nick in self.importantDataForUsers:
            user = Users.objects.create_user(nick, email, 'TruePasswd56')
            userList.append(user)
        
        return userList
    
    def generateFile(self, filename):
        filepath = './media/' + filename
        
        try:
            f = open(filepath, 'x')
            f.write('Contenido del fichero para probar el Adjunto')
            f.close()
        except FileExistsError:
            f = open(filepath, 'rb')

        return filename
    
#---------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                T  E  S  T  S
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testNotice(self):
        userList = self.setup_Users()
        date = '01-03-2000 21:40:53'
        file = self.generateFile('attached.txt')

        noticeNow = models.Notice(
            Creador = userList[0],
            Destino = NoticeScope.TODOS,
            Titulo = 'titulo',
            Texto = 'texto en \n varias líneas.',
            Adjunto = None,
            #FechaCreacion = timezone.now(),
        )

        noticeDate = models.Notice(
            Creador = userList[1],
            Destino = NoticeScope.TODOS,
            Titulo = 'datitulo',
            Texto = 'texto en \n varias líneas.',
            Adjunto = file,
            FechaCreacion = timezone.make_aware(datetime.strptime(date, '%d-%m-%Y %H:%M:%S')),
        )

        noticeNow.save()
        noticeDate.save()

        nowInstance = models.Notice.objects.get(id=1)
        dateInstance = models.Notice.objects.get(id=2)

        self.assertEquals(userList[0], nowInstance.Creador)
        self.assertEquals(noticeNow.Destino, nowInstance.Destino)
        self.assertEquals(noticeNow.Titulo, nowInstance.Titulo)
        self.assertEquals(noticeNow.Texto, nowInstance.Texto)
        self.assertEquals(nowInstance.Adjunto.name, '')
        self.assertTrue(timezone.make_aware(datetime.strptime(date, '%d-%m-%Y %H:%M:%S')) < nowInstance.FechaCreacion < timezone.now())

        attachedFile = open(dateInstance.Adjunto.path, 'br')

        self.assertIsNotNone(attachedFile)
        self.assertEquals(attachedFile.read(), b'Contenido del fichero para probar el Adjunto')

        self.assertEquals(dateInstance.Creador, userList[1])
        self.assertEquals(dateInstance.Destino, noticeDate.Destino)
        self.assertEquals(dateInstance.Titulo, noticeDate.Titulo)
        self.assertEquals(dateInstance.Texto, noticeDate.Texto)
        self.assertEquals(dateInstance.FechaCreacion, noticeDate.FechaCreacion)

        attachedFile.close()
        os.remove(dateInstance.Adjunto.path) #eliminar fichero


#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testVistos(self):
        userList = self.setup_Users()
        date = '01-03-2000 21:40:53'

        noticeNow = models.Notice(
            Creador = userList[0],
            Destino = NoticeScope.TODOS,
            Titulo = 'titulo',
            Texto = 'texto en \n varias líneas.',
            Adjunto = None,
            #FechaCreacion = timezone.now(),
        )

        noticeDate = models.Notice(
            Creador = userList[1],
            Destino = NoticeScope.TODOS,
            Titulo = 'datitulo',
            Texto = 'texto en \n varias líneas.',
            Adjunto = None,
            FechaCreacion = timezone.make_aware(datetime.strptime(date, '%d-%m-%Y %H:%M:%S')),
        )

        noticeNow.save()
        noticeDate.save()

        visto1 = models.Vistos(
            Notice = noticeNow,
            User = userList[0],
        )

        visto2 = models.Vistos(
            Notice = noticeNow,
            User = userList[2],
        )

        visto3 = models.Vistos(
            Notice = noticeDate,
            User = userList[2],
        )

        visto1.save()
        visto2.save()
        visto3.save()

        vistos1 = models.Vistos.objects.get(User=userList[0])
        vistos2 = models.Vistos.objects.filter(User=userList[2])

        self.assertIsNotNone(vistos1)
        self.assertEquals(vistos1.Notice, noticeNow)

        self.assertEquals(vistos2.count(), 2)

        #------- ERROR CASES -------

        with self.assertRaises(IntegrityError):
            vistoDouble = models.Vistos(
                Notice = noticeNow,
                User = userList[0],
            )
            vistoDouble.save()