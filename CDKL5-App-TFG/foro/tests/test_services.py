from datetime import datetime
from django.utils import timezone

from django.test import TransactionTestCase

from foro.models import Post
from foro.forms import newEntryForm, responseForm
from foro import services
from login.constants import RolUsuario, Relaciones
from login import models as lm

from django.core.exceptions import ValidationError

class testModel(TransactionTestCase):
    reset_sequences = True # evitar confilctos de ids autogenerados entre test cases

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

    tutorResponse = lm.Users(
        username= 'tutorResponse',
        email='tutorResponse@email.com',
        first_name='Tutor',
        last_name='Apellidos Response',
        user_role=RolUsuario.USUARIO,
        incomplete=False,
        is_active=True,
        is_staff=False,
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

    tutorPost = Post(
        Creador = tutor,
        Titulo = 'Post Padre',
        Texto = 'Texto de prueba',
        RespuestaDe = None,
        FechaCreacion = timezone.make_aware(datetime.strptime('19/09/22 10:30:01', '%d/%m/%y %H:%M:%S')),
    )

    tutorPostWithResponse = Post(
        Creador = tutor,
        Titulo = 'Post Resp',
        Texto = 'Texto de prueba y respuesta abajo',
        RespuestaDe = None,
        FechaCreacion = timezone.make_aware(datetime.strptime('19/09/22 10:32:01', '%d/%m/%y %H:%M:%S')),
    )

    tutorResponsePost = Post(
        Creador = tutorResponse,
        Titulo = 'Post Resp',
        Texto = 'Texto de prueba y respuesta abajo',
        RespuestaDe = tutorPostWithResponse,
        FechaCreacion = timezone.make_aware(datetime.strptime('19/09/22 10:35:01', '%d/%m/%y %H:%M:%S')),
    )

    def setUpDB(self):

        self.tutor.save()
        self.tutorResponse.save()
        self.amigo.save()

        self.tutorPost.save()
        self.tutorPostWithResponse.save()
        self.tutorResponsePost.save()

        usersCount = lm.Users.objects.all().count()
        postsCount = Post.objects.all().count()

        self.assertEquals(usersCount, 3)
        self.assertEquals(postsCount, 3)

#---------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                T  E  S  T  S
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetPostById(self):
        self.setUpDB()

        #------- TEST CASES -------

        postInstance = services.getPostByID(self.tutorPost.id)

        self.assertIsNotNone(postInstance)

        self.assertEquals(postInstance.Creador, self.tutorPost.Creador)
        self.assertEquals(postInstance.Titulo, self.tutorPost.Titulo)
        self.assertEquals(postInstance.Texto, self.tutorPost.Texto)
        self.assertEquals(postInstance.RespuestaDe, self.tutorPost.RespuestaDe)
        self.assertEquals(postInstance.FechaCreacion, self.tutorPost.FechaCreacion)

        #--------------------------

        postInstance = services.getPostByID(self.tutorResponsePost.id)

        self.assertIsNotNone(postInstance)

        self.assertEquals(postInstance.Creador, self.tutorResponsePost.Creador)
        self.assertEquals(postInstance.Titulo, self.tutorResponsePost.Titulo)
        self.assertEquals(postInstance.Texto, self.tutorResponsePost.Texto)
        self.assertEquals(postInstance.RespuestaDe, self.tutorResponsePost.RespuestaDe)
        self.assertEquals(postInstance.FechaCreacion, self.tutorResponsePost.FechaCreacion)

        #------- ERROR CASES -------

        with self.assertRaises(ValidationError):
            services.getPostByID(8) #id de post no existente

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testgetAllForoData(self):
        posts = services.getAllForoData()

        self.assertIsNone(posts) #lista vacia

        #--------------------------

        self.setUpDB()

        #------- TEST CASES -------

        posts = services.getAllForoData()

        for (parent, respList) in posts:
            if len(respList) > 0:
                resp = list(respList)[0]

                self.assertEquals(resp.Creador, self.tutorResponsePost.Creador)
                self.assertEquals(resp.Titulo, self.tutorResponsePost.Titulo)
                self.assertEquals(resp.Texto, self.tutorResponsePost.Texto)
                self.assertEquals(resp.RespuestaDe, self.tutorResponsePost.RespuestaDe)
                self.assertEquals(resp.FechaCreacion, self.tutorResponsePost.FechaCreacion)

                self.assertEquals(parent.Creador, self.tutorPostWithResponse.Creador)
                self.assertEquals(parent.Titulo, self.tutorPostWithResponse.Titulo)
                self.assertEquals(parent.Texto, self.tutorPostWithResponse.Texto)
                self.assertEquals(parent.RespuestaDe, self.tutorPostWithResponse.RespuestaDe)
                self.assertEquals(parent.FechaCreacion, self.tutorPostWithResponse.FechaCreacion)

            else:
                
                self.assertEquals(parent.Creador, self.tutorPost.Creador)
                self.assertEquals(parent.Titulo, self.tutorPost.Titulo)
                self.assertEquals(parent.Texto, self.tutorPost.Texto)
                self.assertEquals(parent.RespuestaDe, self.tutorPost.RespuestaDe)
                self.assertEquals(parent.FechaCreacion, self.tutorPost.FechaCreacion)


#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testPublishPost(self):
        self.setUpDB()

        #------- TEST CASES -------

        titulo = 'postNuevo'
        texto = 'texto de \n prueba con \n varias lineas'

        postFormData = {
            'titulo': titulo,
            'texto': texto,
        }

        postForm = newEntryForm(postFormData)

        self.assertTrue(postForm.is_valid())

        services.publishPost(postForm, self.tutor)

        post = Post.objects.get(Creador=self.tutor, Titulo=titulo)

        self.assertIsNotNone(post)

        self.assertEquals(post.Creador, self.tutor)
        self.assertEquals(post.Titulo, titulo)
        self.assertEquals(post.Texto, texto)
        self.assertIsNone(post.RespuestaDe)
        self.assertTrue(self.tutorPost.FechaCreacion < post.FechaCreacion < timezone.now())


#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testPublishResponse(self):
        self.setUpDB()

        #------- TEST CASES -------

        titulo = 'Respuesta a: ' + self.tutorPost.Titulo #el titulo se auto-genera recibiendo el titulo del post padre

        texto = 'texto de respuesta \n en varias lineas'

        respFormData = {
            'texto': texto,
        }

        respForm = responseForm(respFormData)
        self.assertTrue(respForm.is_valid())
        
        services.publishResponse(respForm, titulo, self.tutor, self.tutorPost) #respuesta a post propio

        post = Post.objects.get(Titulo=titulo, Creador=self.tutor)

        self.assertIsNotNone(post)

        self.assertEquals(post.Creador, self.tutor)
        self.assertEquals(post.Titulo, titulo)
        self.assertEquals(post.Texto, texto)
        self.assertEquals(post.RespuestaDe, self.tutorPost)
        self.assertTrue(self.tutorPost.FechaCreacion < post.FechaCreacion < timezone.now())

        #--------------------------

        respFormData = {
            'texto': texto,
        }

        respForm = responseForm(respFormData)
        self.assertTrue(respForm.is_valid())
        
        services.publishResponse(respForm, titulo, self.tutorResponse, self.tutorPost) #respuesta a Post de otro usuario

        post = Post.objects.get(Titulo=titulo, Creador=self.tutorResponse)

        self.assertIsNotNone(post)

        self.assertEquals(post.Creador, self.tutorResponse)
        self.assertEquals(post.Titulo, titulo)
        self.assertEquals(post.Texto, texto)
        self.assertEquals(post.RespuestaDe, self.tutorPost)
        self.assertTrue(self.tutorPost.FechaCreacion < post.FechaCreacion < timezone.now())

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testGetOwnedForoData(self):
        self.setUpDB()

        #------- TEST CASES -------

        posts = services.getOwnedForoData(self.tutor)

        self.assertIsNotNone(posts)
        self.assertTrue(len(posts), 2)

        for post in posts:
            self.assertEquals(post.Creador, self.tutor)

        #--------------------------

        posts = services.getOwnedForoData(self.tutorResponse)

        self.assertIsNotNone(posts)
        self.assertTrue(len(posts), 1)

        for post in posts:
            self.assertEquals(post.Creador, self.tutorResponse)

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testUpdatePost(self):
        self.setUpDB()

        #------- TEST CASES -------

        titulo = 'postEditado'
        texto = 'texto de post editado para cambiarlo.'

        prevEdit = timezone.now()

        postFormData = {
            'titulo': titulo,
            'texto': texto,
        }

        postForm = newEntryForm(postFormData)
        self.assertTrue(postForm.is_valid())

        services.updatePost(postForm, self.tutorPost.id) #editar post padre

        post = Post.objects.get(id=self.tutorPost.id)

        self.assertIsNotNone(post)

        self.assertEquals(post.Creador, self.tutor)
        self.assertEquals(post.Titulo, titulo)
        self.assertEquals(post.Texto, texto)
        self.assertIsNone(post.RespuestaDe)
        self.assertTrue(prevEdit < post.FechaCreacion < timezone.now())

        #--------------------------

        prevEdit = timezone.now()

        postFormData = {
            'texto': texto,
        }

        postForm = responseForm(postFormData)
        self.assertTrue(postForm.is_valid())

        services.updatePost(postForm, self.tutorResponsePost.id) #editar respuesta

        post = Post.objects.get(id=self.tutorResponsePost.id)

        self.assertIsNotNone(post)

        self.assertEquals(post.Creador, self.tutorResponse)
        self.assertEquals(post.Titulo, self.tutorResponsePost.Titulo) #titulo de respuesta no se edita
        self.assertEquals(post.Texto, texto)
        self.assertEquals(post.RespuestaDe, self.tutorPostWithResponse)
        self.assertTrue(prevEdit < post.FechaCreacion < timezone.now())

#---------------------------------------------------------------------------------------------------------------------------------------------------

    def testDeletePost(self):
        self.setUpDB()

        #------- TEST CASES -------

        services.deletePost(self.tutorPost.Creador, self.tutorPost.id) #borrar post sin respuestas

        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(Titulo=self.tutorPost, Creador=self.tutorPost.Creador)

        #--------------------------

        services.deletePost(self.tutorResponsePost.Creador, self.tutorResponsePost.id) #borrar respuesta de un post (sin borrar post)

        parent = Post.objects.get(id=self.tutorPostWithResponse.id)
        self.assertIsNotNone(parent)

        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(Titulo=self.tutorResponsePost, Creador=self.tutorResponsePost.Creador)

        #--------------------------

        self.tutorResponsePost.save() #rehacer respuesta

        services.deletePost(self.tutorPostWithResponse.Creador, self.tutorPostWithResponse.id) #borrar post y respuestas

        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(Titulo=self.tutorResponsePost, Creador=self.tutorResponsePost.Creador)

        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(Titulo=self.tutorPostWithResponse, Creador=self.tutorPostWithResponse.Creador)


        #------- ERROR CASES -------

        with self.assertRaises(ValidationError):
            services.deletePost(self.amigo, self.tutorPost.id)

#---------------------------------------------------------------------------------------------------------------------------------------------------
