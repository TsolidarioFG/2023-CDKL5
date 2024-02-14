from django import forms

class hospManageForm(forms.Form):
    def __init__(self, allList, vincList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for item in allList:
            if item.Nombre in vincList:
                self.fields[item.Nombre] = forms.BooleanField(required=False, label=item.Nombre, widget=forms.CheckboxInput(attrs={'checked': ''}))
            else:
                self.fields[item.Nombre] = forms.BooleanField(required=False, label=item.Nombre, widget=forms.CheckboxInput())

class payPendForm(forms.Form):
    def __init__(self, allList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for item in allList:
            if item.Pendiente:
                self.fields[item.Identificador] = forms.BooleanField(required=False, label=item.Identificador, widget=forms.CheckboxInput(attrs={'checked': ''}))
            else:
                self.fields[item.Identificador] = forms.BooleanField(required=False, label=item.Identificador, widget=forms.CheckboxInput())

class payVarsForm(forms.Form):
    minAmigo = forms.FloatField(required=True, widget=forms.NumberInput(attrs={'placeholder': 'Mínimo importe de un Amigo (€)*'}), label='')
    tarSocio = forms.FloatField(required=True, widget=forms.NumberInput(attrs={'placeholder': 'Tarifa de usuarios con socio b. (€)*'}), label='')
    payDate = forms.DateField(required=True, widget=forms.DateInput(attrs={'placeholder': 'Fecha de Cobro', 'id': 'datepicker', }, format='%d/%m/%Y'))