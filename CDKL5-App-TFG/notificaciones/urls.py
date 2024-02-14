from notificaciones import views
from django.urls import path, re_path

urlpatterns = [
    path('', views.notices_view, name='notices'),
    path('new', views.sendNotice_view, name='newNotice'),
    re_path('^viewed/(?P<noticeId>\w+)$', views.updateViewed_view, name='updateViewed'),
]