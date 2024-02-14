from dataManagement import views
from django.urls import path, re_path

urlpatterns = [
    path('users', views.displayUserList_view, name='displayUserList'),
    path('payvars', views.editGeneralVars_view, name='editGeneralVars'),
    re_path('^users/(?P<userProf_id>\w+)$', views.editUser_view, name='EditUser'),
    re_path('^(?P<data_type>\w+)$', views.optionalDisplay_view, name='displayOptionalData'),
]