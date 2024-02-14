from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.defaults import page_not_found, bad_request, server_error

from login.forms import SocioForm, TutorForm, AmigoBankForm, SocioBankForm, AmigoForm, LoginForm, askEmailForm, PasswordForm, HospitalForm
from login.constants import RolUsuario
from login import services
from notificaciones import services as nsrv

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout

from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.exceptions import SuspiciousOperation

from dataManagement import services as dms

from django.utils import timezone
# Create your views here.

# Base login view
def home_view(request):
    if request.user.is_authenticated:
        #return render(request,"login/home.html", {'user': request.user})
        return HttpResponseRedirect('/foro')
    else:
        return render(request,"login/home.html")

def signupSocio_view(request):
    if request.method == 'POST':
        form = SocioForm(request.POST)
        try:
            socioData = services.signupSocio(form)
            request.session['socioCode'] = socioData['code']
            return HttpResponseRedirect('/signup/tutor?id_socio=%d' %(socioData['id']))
        except ValidationError as error:
            messages.error(request, error.message)
        return render(request, 'signup/Socio.html', {'form': form})
    else:
        form = SocioForm()
        return render(request, 'signup/Socio.html', {'form': form})

def addExistentSocio_view(request):
    id = ''
    code = ''
    if request.method == 'GET':
        id = request.GET.get('idSocio')
        code = request.GET.get('socioCode')
        if id and code:
            try: 
                socioRef = services.validateSocioVinculation(id, code)
                request.session['socioCode'] = code
                return HttpResponseRedirect('/signup/tutor?id_socio=%d' %(socioRef.id))
            except ValidationError as exn:
                message = exn.message
                return render(request, 'signup/SocioSearch.html', {'message': message})
    return render(request, 'signup/SocioSearch.html')

def signup_view(request, user_type):
    if request.method == 'POST':
        if user_type == 'tutor':
            form = TutorForm(request.POST)
            socio = request.session['socio']
            userRole = RolUsuario.USUARIO
        elif user_type == 'amigo':
            form = AmigoForm(request.POST)
            socio = None
            userRole = RolUsuario.AMIGO
        else:
            return render(request, 'error.html', {})
        try:
            (user, rawPasswd) = services.completeUserForm(form, userRole)
            services.saveUserProfile(form, idSocio=socio, usuarioVincular=user) # guardar en base de datos el resto de datos
            request.session['password'] = rawPasswd
            text = services.sendConfirmationEmail(user.email)

            return render(request, 'signup/emailSent.html', {'text': text, 'title': 'Datos Guardados con éxito'})

        except ValidationError as error:
                print(error)
                messages.error(request, error.message)
        except services.SeveralErrorMessagesException as exn:
            print(exn)
            for error in exn.errorList:
                messages.error(request, error)
        if user_type == 'tutor':
            socioCode = request.session['socioCode']
            return render(request, 'signup/Tutor.html', {'form': form, 'id_socio': socioCode})
        elif user_type == 'amigo':
            return render(request, 'signup/Amigo.html', {'form': form}) #End Caso POST 
        
    else: #Peticion inicial
        if user_type == 'tutor':
            socioCode = request.session['socioCode']
            form = TutorForm()
            socio = request.GET["id_socio"]
            request.session['socio'] = socio
            socioCode = request.session['socioCode']
            return render(request, 'signup/Tutor.html', {'form': form, 'id_socio': socioCode})
        elif user_type == 'amigo':
            form = AmigoForm()
            return render(request, 'signup/Amigo.html', {'form': form})
        else:
            return render(request, 'error.html', {})


def signupBank_view(request, action='default'):
    payVarsDict = dms.getGeneralVars()
    if request.method == 'POST': #petición con datos a sobreescribir
        user = request.user
        socio = services.getAsociado(user.id)
        socioCode = None
        if socio == None: #Amigo
            HTMLpage = 'signup/AmigoBank.html'
            form = AmigoBankForm(request.POST, request.FILES)
        else: #Socio+tutor
            socioCode = request.session['socioCode']
            HTMLpage = 'signup/SocioBank.html'
            form = SocioBankForm(request.POST, request.FILES)
        try:
            services.signupBankData(bankform=form, userId=user.id, minAmigo=payVarsDict['minAmigo'])
            if socio:
                del request.session['socioCode']
                return render(request, 'signup/done.html', {'id': socio.id, 'code': socioCode})
            return render(request, 'signup/done.html', {'id': 0, 'code': socioCode}) #amigo
    
        except ValidationError as error:
            form.add_error(None, error.message)
        except services.SeveralErrorMessagesException as exn:
            for error in exn.errorList:
                messages.error(request, error)
        return render(request, HTMLpage, {'form': form})

    else: # peticion inicial
        user = request.user
        socio = services.getAsociado(user.id)
        if socio == None: #Amigo
            form = AmigoBankForm()
            return render(request, 'signup/AmigoBank.html', {'form': form, 'user': user})
        else: #Socio+tutor
            socioCode = request.session['socioCode']
            if services.hasBankInfo(socio):
                if action == 'continue': #Con datos que se quieren sobreescribir
                    user = request.user
                    form = SocioBankForm()
                    return render(request, 'signup/SocioBank.html', {'form': form, 'user': user, 'tarSocio': payVarsDict['tarSocio']})
                elif action == 'skip': #Con datos que se quieren mantener
                    return render(request, 'signup/done.html', {'id': socio.id, 'code': socioCode})
                #Caso sin decisión tomada
                
                return render(request, 'signup/BankConfirmation.html', {'user': user, 'id_socio': socioCode})
            #endif
            #Caso general (socio sin información)
            form = SocioBankForm()
            return render(request, 'signup/SocioBank.html', {'form': form, 'user': user, 'tarSocio': payVarsDict['tarSocio']})

def signupOptional_view(request, entity_type):
    if request.method == 'POST':
        if request.session['entity'] == 'Hospitales':
            form = HospitalForm(request.POST)

        if form.is_valid():
            try:
                text = services.signupOptData(form, request.user.id, request.session['entity'])
                messages.success(request, text)
                del request.session['entity']
                if 'SaveContinue' in request.POST:
                    return HttpResponseRedirect('/signup/opt/' + entity_type)
                else:
                    return HttpResponseRedirect('/manage/' + entity_type)
            except ValidationError as error:
                messages.error(request, error.message)
        
        return render(request, 'signup/Optional.html', {'form': form, 'entity': request.session['entity']})
    
    else: #caso inicial
        if entity_type == 'hospitals':
            form = HospitalForm()
            request.session['entity'] = 'Hospitales'
        else:
            raise SuspiciousOperation #excepción que llama a error 400-bad request
        return render(request, 'signup/Optional.html', {'form': form, 'entity': request.session['entity']})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                if user is not None: #si el usuario ha sido autenticado por algún backend
                    login(request, user)
                    return HttpResponseRedirect('/')
                raise ValidationError('Usuario y/o contraseña Incorrectos. Por favor, inténtelo de nuevo.')
            except ValidationError as error:
                messages.error(request, error.message)
        return render(request, 'login/Login.html', {'form': form})
    else:
        form = LoginForm()
        return render(request, 'login/Login.html', {'form': form})
    
def logoutConfirm_view(request):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = services.getNotices(request.user)
    if request.user.is_authenticated:
        print(request.GET)
        return render(request, 'login/Logout.html', {'pendantNo': pendant, 'canNotices': canReceiveNotices})
    else:
        return render(request, 'userNotAuthenticated.html', {})
    
def logout_view(request):
    if request.user.is_authenticated:
        services.addLog(request.user)
        logout(request)
        messages.success(request, "Ha cerrado la sesión.")    
    return HttpResponseRedirect("/")

def requestPwdChange_view(request):
    if request.method == 'POST':
        form = askEmailForm(request.POST)
        try:
            message = services.sendResetEmail(form)
            return render(request, 'signup/emailSent.html', {'text': message, 'title': 'Enviado E-mail de confirmación'})
        except ValidationError as exn:
            for error in exn.messages:
                messages.error(request, error)
        return render(request, 'login/changePwd.html', {'form': form})
    else:
        form = askEmailForm()
        return render(request, 'login/changePwd.html', {'form': form})
    
def activate_view(request, activation_type, uidb64, token):
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        email = request.session['userEmail']
        try:
            newPassword = services.changeUserPassword(form, email)
            messages.success(request, 'Contraseña cambiada con éxito.')
            user = authenticate(request, email=email, password=newPassword)
            if user is not None: #si el usuario ha sido autenticado por algún backend
                login(request, user)
                return HttpResponseRedirect('/')
            messages.error(request, 'No ha podido efectuarse el Login. Por favor, inténtelo manualmente con la nueva contraseña.')
            return HttpResponseRedirect('/')
        except ValidationError as exn:
            for error in exn.messages:
                messages.error(request, error)
        return render(request, 'login/changePwd.html', {'form': form})
    else: #caso inicial
        user = services.activate(uidb64, token) #confirmar que token es valido y obtener usuario asociado
        if user is not None:
            if activation_type == 'passwordReset':
                    request.session['userEmail'] = user.email
                    form = PasswordForm()
                    return render(request, 'login/changePwd.html', {'form': form})
                
            elif activation_type == 'signupConfirm':
                rawPassword = request.session['password']
                user = authenticate(request, email=user.email, password=rawPassword)
                if user is not None: #si el usuario ha sido autenticado por algún backend
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    #del request.session['password']
                    return HttpResponseRedirect('/signup/bank')
                
            else:
                raise SuspiciousOperation #excepción que llama a error 400-bad request
        return HttpResponse('Token Invalido o ya usado.')
    

    #---------------------------------------------------------------------------------------------

def error_400_view(request, exception):
    template = 'errors/error400.html'
 
    return render(request, template, status=400)

def error_404_view(request, exception):
    template = 'errors/error404.html'
 
    return render(request, template, status=404)


def error_500_view(request):
    template = 'errors/error500.html'
 
    return render(request, template, status=500)