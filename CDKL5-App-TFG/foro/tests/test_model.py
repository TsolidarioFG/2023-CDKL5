from datetime import datetime
from django.test import TransactionTestCase
from django.utils import timezone


from login.models import Users
from foro import models

class testModel(TransactionTestCase):
    reset_sequences = True # evitar confilctos de ids autogenerados entre test cases
    importantDataForUsers = [('email1@email.com', 'username1'), ('email2@email.com', 'username2'), ('email3@email.com', 'usename3')]
    Titulo = 'Titulo de prueba'
    TextoVariasLineas = 'texto de prueba con varias cosas \n en varias líneas \n hecho por una persona'
    Texto = 'Texto de prueba para posts'

    def setup_Users(self): #crear usuarios para hacer de creadores de posts
        userList = []
        for email,nick in self.importantDataForUsers:
            user = Users.objects.create_user(nick, email, 'TruePasswd56')
            userList.append(user)
        
        return userList

#---------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                T  E  S  T  S
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testPost(self):
        creatorList = self.setup_Users()
        date = '01-03-2000 21:40:53'

        postNowInstance = models.Post(
            Creador= creatorList[0],
            Titulo= self.Titulo,
            Texto= self.TextoVariasLineas,
        )
        postNowInstance.save()

        postDateInstance = models.Post(
            Creador= creatorList[1],
            Titulo= self.Titulo + '2',
            Texto= self.Texto,
            FechaCreacion= timezone.make_aware(datetime.strptime(date, '%d-%m-%Y %H:%M:%S')),
        )
        postDateInstance.save()

        postNow = models.Post.objects.get(id=1)
        postDate = models.Post.objects.get(id=2)

        self.assertEquals(creatorList[0], postNow.Creador)
        self.assertEquals(self.Titulo, postNow.Titulo)
        self.assertEquals(self.TextoVariasLineas, postNow.Texto)
        self.assertEquals(timezone.now().date(), postNow.FechaCreacion.date())

        self.assertEquals(creatorList[1], postDate.Creador)
        self.assertEquals(self.Titulo + '2', postDate.Titulo)
        self.assertEquals(self.Texto, postDate.Texto)
        self.assertEquals(timezone.make_aware(datetime.strptime(date, '%d-%m-%Y %H:%M:%S')), postDate.FechaCreacion)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testResponseToPost(self):
        creatorList = self.setup_Users()
        date = '01-03-2000 21:40:53'

        postDateInstance = models.Post(
            Creador= creatorList[1],
            Titulo= self.Titulo + '2',
            Texto= self.Texto,
            FechaCreacion= timezone.make_aware(datetime.strptime(date, '%d-%m-%Y %H:%M:%S')),
        )
        postDateInstance.save()

        postDate = models.Post.objects.get(id=1)

        self.assertEquals(creatorList[1], postDate.Creador)
        self.assertEquals(self.Titulo + '2', postDate.Titulo)
        self.assertEquals(self.Texto, postDate.Texto)
        self.assertIsNone(postDate.RespuestaDe)
        self.assertEquals(timezone.make_aware(datetime.strptime(date, '%d-%m-%Y %H:%M:%S')), postDate.FechaCreacion)

        postRespInstance = models.Post(
            Creador= creatorList[2],
            Titulo= 'Respuesta de Post',
            Texto= self.Texto,
            RespuestaDe= postDate,
            FechaCreacion= timezone.make_aware(datetime.strptime(date, '%d-%m-%Y %H:%M:%S')),
        )
        postRespInstance.save()

        postResp = models.Post.objects.get(id=2)

        self.assertEquals(creatorList[2], postResp.Creador)
        self.assertEquals('Respuesta de Post', postResp.Titulo)
        self.assertEquals(self.Texto, postResp.Texto)
        self.assertEquals(postDate, postResp.RespuestaDe)
        self.assertEquals(timezone.make_aware(datetime.strptime(date, '%d-%m-%Y %H:%M:%S')), postResp.FechaCreacion)



#---------------------------------------------------------------------------------------------------------------------------------------------------