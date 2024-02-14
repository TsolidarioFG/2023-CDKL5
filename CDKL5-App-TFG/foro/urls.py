from foro import views
from django.urls import path, re_path

urlpatterns = [
    path('', views.foro_view, name='foro'),
    path('new', views.newForoEntry_view, name='newEntry'),
    path('posted', views.editOwnedPosts_view, name='viewOwnedPosts'),
    re_path('^edit/(?P<postId>\w+)$', views.editPost_view, name='EditPost'),
    re_path('^delete/(?P<postId>\w+)$', views.deletePost_view, name='DeletePost'),
    re_path('^response/(?P<originalPost>\w+)$', views.responseTo_view, name='EditUser'),

]