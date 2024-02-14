from django.utils import timezone
from notificaciones import models, constants

def getNoticeById(noticeId):
    return models.Notice.objects.get(id=noticeId)

def getAllNotices(currentUser):
    if currentUser.is_staff:
        notices = models.Notice.objects.filter(FechaCreacion__gt=currentUser.date_joined).order_by('-FechaCreacion')
    else:
        notices = models.Notice.objects.filter(Destino=constants.NoticeScope.TODOS, FechaCreacion__gt=currentUser.date_joined).order_by('-FechaCreacion')
    vistos = models.Vistos.objects.filter(User=currentUser).values_list('Notice', flat=True)
    return (notices, vistos)

def sendNotice(noticeForm, currentUser):
    notice = models.Notice(
        Creador = currentUser,
        Destino = noticeForm.cleaned_data['destino'],
        Titulo = noticeForm.cleaned_data['titulo'],
        Texto = noticeForm.cleaned_data['texto'],
        Adjunto = noticeForm.cleaned_data['adjunto'],
        FechaCreacion = timezone.now(),
    )
    notice.save()
    return 'Notificación Enviada Correctamente.'

def updateViewed(noticeId, user):
    notice = getNoticeById(noticeId)
    newInstance = models.Vistos(
        Notice = notice, 
        User = user,
    )
    try:
        newInstance.save() #guardar en vistos
    except Exception: #si ya está guardada, no hacer nada
        pass
    return

def getPendantNotices(user):
    if user.is_authenticated:
        vistos = models.Vistos.objects.filter(User=user).count()
        if user.is_staff:
            allNotices = models.Notice.objects.filter(FechaCreacion__gt=user.date_joined).count() #sólo tener en cuenta notificaciones posteriores al registro
        else:
            allNotices = models.Notice.objects.filter(Destino=constants.NoticeScope.TODOS, FechaCreacion__gt=user.date_joined).count()
        return allNotices - vistos
    return 0