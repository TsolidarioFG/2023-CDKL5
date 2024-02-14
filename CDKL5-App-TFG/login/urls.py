from login import views
from django.urls import path, include, re_path

urlpatterns = [
    
    path('signup/socio', views.signupSocio_view, name='signupSocio'),
    path('signup/socioID', views.addExistentSocio_view, name='ExistentSocio'),
    path('signup/bank', views.signupBank_view, name='signupBank'),
    re_path('^signup/opt/(?P<entity_type>\w+)$', views.signupOptional_view, name='signupOptional'),
    re_path('^signup/bank/(?P<action>\w+)$', views.signupBank_view, name='BankConfirmation'),
    re_path('^signup/(?P<user_type>\w+)/$', views.signup_view, name='GenericSignup'),
    path('login/', views.login_view, name='login'),
    path('login/changepwd', views.requestPwdChange_view, name='ChangePassword'),
    re_path('^(?P<activation_type>\w+)/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,6}-[0-9A-Za-z]{1,32})$', views.activate_view, name='passwordChangeActivate'),
    path('logout/confirm', views.logoutConfirm_view, name='LogoutConfirm'),
    path('logout/', views.logout_view, name='Logout'),
    path('accounts/', include('allauth.urls')),
    path("", views.home_view, name="home"),
] 
