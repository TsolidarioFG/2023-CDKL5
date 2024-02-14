from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
# Create your views here.

from notificaciones import services as nsrv
from login import services as lsrv
from dataManagement import services as dmservices
from login.constants import RolUsuario
from dataManagement import forms

def optionalDisplay_view(request, data_type):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.method == 'POST':
        socio = lsrv.getAsociado(request.user.id)   
        if data_type == 'hospitals':
            querySets = lsrv.getHospLists(socio)
        form_items = list(request.POST.keys()) #Obtener selección de items marcados por el usuario
        form_items.remove('csrfmiddlewaretoken')#eliminar tag del csrf
        form_items.remove('changeVinculations')#eliminar tag del boton submit
        try:
            text = lsrv.updateVinculations(previousSelection=list(querySets['vinc']), newSelection=form_items, socio=socio, type=data_type)
            messages.success(request, text)
        except lsrv.SeveralErrorMessagesException as exn:
            for error in exn.errorList:
                messages.error(request, error)
        return HttpResponseRedirect('/manage/' + data_type)


    else: #Caso inicial
        if request.user.is_authenticated:
            socio = lsrv.getAsociado(request.user.id)
            if data_type == 'hospitals':
                querySets = lsrv.getHospLists(socio)
                viewPath = 'optional/hospListDisplay.html'
                form = forms.hospManageForm(allList=querySets['all'], vincList=querySets['vinc'])
            else:
                viewPath = 'wrongTypeError.html'
            return render(request, viewPath, {'iterables': zip(querySets['all'], form), 'emptyList': (not querySets['all']), 'pendantNo': pendant, 'canNotices': canReceiveNotices})
        return render(request, 'userNotAuthenticated.html', {'pendantNo': pendant, 'canNotices': canReceiveNotices})


def displayUserList_view(request):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.user.is_authenticated:
        payVarsDict = dmservices.getGeneralVars()
        if request.method == 'POST' and request.user.user_role == RolUsuario.TESORERIA:
            options = [2, 5, 10, 25, 50, 100]
            selected = request.GET.get('perPage')
            if not selected:
                selected = 10
            options.remove(int(selected))

            form_items = list(request.POST.keys()) #Obtener selección de items marcados por el usuario
            form_items.remove('csrfmiddlewaretoken')#eliminar tag del csrf
            form_items.remove('updatePays')#eliminar tag del boton submit
            print(form_items)

            text = lsrv.updatePays(form_items) # actualizar booleano PagoPendiente
            messages.success(request, text)
            return HttpResponseRedirect('/manage/users')

        if request.user.user_role in [RolUsuario.SECRETARIA, RolUsuario.PRESIDENCIA]: #vista secretario
            options = [2, 5, 10, 25, 50, 100]
            selected = request.GET.get('perPage')
            if not selected:
                selected = 10
            options.remove(int(selected))
            paginatedList = dmservices.getPaginatedSecretaryList(selected, request.GET.get('users-query'))
            page_number = request.GET.get("page")
            page_obj = paginatedList.get_page(page_number)
            return render(request, 'secretario/userListDisplay.html', {'page_obj': page_obj, 'options': options, 'selected': selected, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
        
        elif request.user.user_role == RolUsuario.TESORERIA: #vista tesorero
            options = [2, 5, 10, 25, 50, 100]
            selected = request.GET.get('perPage')
            if not selected:
                selected = 10
            options.remove(int(selected))
            paginatedList = dmservices.getPaginatedTreasuryList(selected, payVarsDict['tarSocio'], request.GET.get('reset'))
            if request.GET.get('reset'):
                messages.success(request, 'Registro de pagos Reiniciado correctamente.')
            page_number = request.GET.get("page")
            page_obj = paginatedList.get_page(page_number)
            form = forms.payPendForm(allList=paginatedList.object_list)
            return render(request, 'tesorero/userListDisplay.html', {'page_obj': page_obj, 'options': options, 'selected': selected, 'payForm': form, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
    return render(request, 'userNotAuthenticated.html', {'pendantNo': pendant, 'canNotices': canReceiveNotices})

def editUser_view(request, userProf_id):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.method == 'POST' and request.user.is_staff:
        forms = lsrv.parseGlobalUpdateData(request.POST, request.FILES, request.session['userIdentifier'])
        #print(forms)
        try:
            message = lsrv.updateData(forms, forms['id'])
            messages.success(request, message)

        except lsrv.ValidationError as error:
            messages.error(request, error.message)
        except lsrv.SeveralErrorMessagesException as exn:
            for error in exn.errorList:
                messages.error(request, error)
        if lsrv.keepsStaff(request.user.id): # caso MUY específico de quitarse privilegios a uno mismo
            try:
                (path, userEntityList) = lsrv.reallocateData(forms)
                return render(request, 'edit/singleUser.html', {'list': userEntityList, 'docPath': path, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
            except lsrv.ValidationError: #Caso de usuario inexistente (inactivo)
                return HttpResponseRedirect('/manage/users')
        return render(request, 'userNotAuthenticated.html', {'pendantNo': pendant, 'canNotices': canReceiveNotices})
    else:
        if request.user.is_staff:
            
            (path, userNick, userEntityList) = dmservices.getAllUserData(userProf_id)
            request.session['userIdentifier'] = userNick
            return render(request, 'edit/singleUser.html', {'list': userEntityList, 'docPath': path, 'pendantNo': pendant, 'canNotices': canReceiveNotices})
    return render(request, 'userNotAuthenticated.html', {'pendantNo': pendant, 'canNotices': canReceiveNotices})

def editGeneralVars_view(request):
    pendant = nsrv.getPendantNotices(request.user)
    canReceiveNotices = lsrv.getNotices(request.user)
    if request.method == 'POST':
        form = forms.payVarsForm(request.POST)
        try:
            text = dmservices.updateGeneralVars(form)
            messages.success(request, text)
            return HttpResponseRedirect('/manage/users')
        except lsrv.SeveralErrorMessagesException as exn:
            for error in exn.errorList:
                messages.error(request, error)
        return HttpResponseRedirect('/manage/payvars')
    else:
        if request.user.is_authenticated and request.user.user_role == RolUsuario.TESORERIA:
            varsDict = dmservices.getGeneralVars()
            form = forms.payVarsForm()
            return render(request, 'edit/payVars.html', {'minAmigo': varsDict['minAmigo'], 'tarSocio': varsDict['tarSocio'], 'payDate': varsDict['payDate'].strftime('%d-%m'), 'form': form, 'pendantNo': pendant, 'canNotices': canReceiveNotices})

    return render(request, 'userNotAuthenticated.html', {'pendantNo': pendant, 'canNotices': canReceiveNotices})