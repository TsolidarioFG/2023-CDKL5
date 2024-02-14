from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
# Create your views here.

from foro import services
from notificaciones import services as nsrv
from login import services as lsrv
from foro.forms import newEntryForm, responseForm
from login.constants import RolUsuario

def foro_view(request):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.user.is_authenticated and request.user.user_role != RolUsuario.AMIGO:
        data = services.getAllForoData()
        return render(request, 'foro.html', {'data': data, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
    return render(request, 'userNotAuthorized.html', {'user': request.user, 'pendantNo': pendant, 'canNotices': canReceiveNotices})

def newForoEntry_view(request):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.user.is_authenticated and request.user.user_role != RolUsuario.AMIGO:
        if request.method == 'POST':
            form = newEntryForm(request.POST)
            if form.is_valid():
                text = services.publishPost(form, request.user)
                messages.success(request, text)
                return HttpResponseRedirect('/foro')
            return render(request, 'newEntry.html', {'form': form, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
        else:
            form = newEntryForm()
            return render(request, 'newEntry.html', {'form': form, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
    return render(request, 'userNotAuthorized.html', {'user': request.user, 'pendantNo': pendant, 'canNotices': canReceiveNotices})

def responseTo_view(request, originalPost):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.user.is_authenticated and request.user.user_role != RolUsuario.AMIGO:
        if request.method == 'POST':
            post = services.getPostByID(originalPost)
            form = responseForm(request.POST)
            if form.is_valid():
                respTitle = 'Respuesta a: ' + post.Titulo
                text = services.publishResponse(form, respTitle, request.user, post)
                messages.success(request, text)
                return HttpResponseRedirect('/foro')
            return render(request, 'responseToPost.html', {'form': form, 'original': post, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
        else:
            post = services.getPostByID(originalPost)
            form = responseForm()
            return render(request, 'responseToPost.html', {'form': form, 'original': post, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
    return render(request, 'userNotAuthorized.html', {'user': request.user, 'pendantNo': pendant, 'canNotices': canReceiveNotices})


def editOwnedPosts_view(request):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.user.is_authenticated and request.user.user_role != RolUsuario.AMIGO:
        data = services.getOwnedForoData(request.user)
        return render(request, 'myPosts.html', {'data': data, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
            
    return render(request, 'userNotAuthorized.html', {'user': request.user, 'pendantNo': pendant, 'canNotices': canReceiveNotices})

def editPost_view(request, postId):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.user.is_authenticated and request.user.user_role != RolUsuario.AMIGO:
        if request.method == 'POST':
            post = services.getPostByID(postId)
            if not post.RespuestaDe:
                form = newEntryForm(request.POST)
            else:
                form = responseForm(request.POST)
            if form.is_valid():
                text = services.updatePost(form, postId)
                messages.success(request, text)
                return HttpResponseRedirect('/foro/posted')
            return render(request, 'editEntry.html', {'form': form, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
        
        else:
            post = services.getPostByID(postId)
            if not post.RespuestaDe:
                postForm = {
                    'titulo': post.Titulo,
                    'texto': post.Texto,
                }
                form = newEntryForm(postForm)
            else:
                postForm = {'texto': post.Texto }
                form = responseForm(postForm)
            return render(request, 'editEntry.html', {'form': form, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
            
    return render(request, 'userNotAuthorized.html', {'user': request.user, 'pendantNo': pendant, 'canNotices': canReceiveNotices})

def deletePost_view(request, postId):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.user.is_authenticated and request.user.user_role != RolUsuario.AMIGO:
        try:
            text = services.deletePost(request.user, postId)
            messages.success(request, text)
        except ValidationError as exn:
            messages.error(request, exn.message)
        return HttpResponseRedirect('/foro/posted')
    return render(request, 'userNotAuthorized.html', {'user': request.user, 'pendantNo': pendant, 'canNotices': canReceiveNotices})