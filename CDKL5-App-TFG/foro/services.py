from django.utils import timezone

from foro import models
from django.core.exceptions import ValidationError

def getPostByID(postId):
    try:
        return models.Post.objects.get(id=int(postId))
    except Exception as exn:
        raise ValidationError('El post referenciado no existe.')

def getAllForoData():
    posts = models.Post.objects.filter(RespuestaDe=None).order_by('-FechaCreacion')
    dataList = []
    for post in posts:
        responses = models.Post.objects.filter(RespuestaDe=post.id).order_by('FechaCreacion')
        dataList.append((post, responses))

    if dataList:
        return dataList
    return None

def publishPost(postForm, creator):
    postInstance = models.Post(
        Creador = creator,
        Titulo = postForm.cleaned_data['titulo'],
        Texto = postForm.cleaned_data['texto'],
    )
    postInstance.save()
    return 'Publicación realizada correctamente.'

def publishResponse(respForm, respTitle, creator, originalPost):
    postInstance = models.Post(
        Creador = creator,
        Titulo = respTitle,
        Texto = respForm.cleaned_data['texto'],
        RespuestaDe = originalPost
    )
    postInstance.save()
    return 'Respuesta publicada correctamente.'

def getOwnedForoData(user):
    ownedPosts = models.Post.objects.filter(Creador=user).order_by('-FechaCreacion')
    return ownedPosts

def updatePost(postForm, postId):
    postToUpdate = getPostByID(postId)
    if not postToUpdate.RespuestaDe:
        postToUpdate.Titulo = postForm.cleaned_data['titulo']
    postToUpdate.Texto = postForm.cleaned_data['texto']
    postToUpdate.FechaCreacion = timezone.now()
    postToUpdate.save()
    return 'Post Actualizado correctamente.'

def deletePost(owner, postId):
    post = getPostByID(postId)
    if post.Creador == owner:
        post.delete()
        return 'Post borrado con éxito.'
    else:
        raise ValidationError('Usuario no propietario del post. No puede borrarse un post creado por otro usuario')