from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from notificaciones import services
from login import services as lsrv
from notificaciones.forms import newNoticeForm
from login.constants import RolUsuario

# Create your views here.

def notices_view(request):
    pendant = services.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.user.is_authenticated and request.user.user_role != RolUsuario.AMIGO:
        (data, vistos) = services.getAllNotices(request.user)
        return render(request, 'general/notices.html', {'data': data, 'vistos': vistos, 'user': request.user, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
    return render(request, 'userNotAuthenticated.html', {'user': request.user, 'pendantNo': pendant, 'canNotices': canReceiveNotices})

def sendNotice_view(request):
    pendant = services.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            form = newNoticeForm(request.POST, request.FILES)
            if form.is_valid():
                text = services.sendNotice(form, request.user)
                messages.success(request, text)
                return HttpResponseRedirect('/notices')
        else:
            form = newNoticeForm()
            return render(request, 'staff/new.html', {'form': form, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
    return render(request, 'userNotAuthenticated.html', {'user': request.user, 'pendantNo': pendant, 'canNotices': canReceiveNotices})

def updateViewed_view(request, noticeId):
    services.updateViewed(noticeId, request.user)
    return HttpResponseRedirect('/notices')